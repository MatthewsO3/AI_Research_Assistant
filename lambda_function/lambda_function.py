from dotenv import load_dotenv
import os
import json
import boto3
import requests
import uuid
from datetime import datetime
import os

load_dotenv()  # Load from .env file
# AWS clients
s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('ResearchResults')

SERPAPI_KEY = os.environ['SERPAPI_KEY']
S3_BUCKET = os.environ['S3_BUCKET']
OLLAMA_ENDPOINT = os.environ['OLLAMA_ENDPOINT']


def search_papers(topic, num_results=3):
    """Search papers using SerpAPI free tier (100/month free)"""
    try:
        url = "https://serpapi.com/search"
        params = {
            "q": f"{topic} research paper",
            "api_key": SERPAPI_KEY,
            "engine": "google",
            "num": num_results,
            "type": "search"
        }
        response = requests.get(url, params=params, timeout=30)
        results = response.json()

        papers = []
        if 'organic_results' in results:
            for result in results['organic_results'][:num_results]:
                papers.append({
                    'title': result.get('title', 'Unknown'),
                    'link': result.get('link', ''),
                    'snippet': result.get('snippet', '')
                })
        return papers
    except Exception as e:
        print(f"Error searching: {e}")
        return []


def summarize_with_ollama(content, topic):
    """Use Ollama (running on EC2) - completely FREE"""
    try:
        # Use phi model (small, free)
        response = requests.post(
            f'{OLLAMA_ENDPOINT}/api/generate',
            json={
                'model': 'phi',
                'prompt': f"Summarize this research about '{topic}' in 3-4 key points:\n\n{content[:1500]}",
                'stream': False,
                'temperature': 0.7
            },
            timeout=60
        )

        if response.status_code == 200:
            result = response.json()
            return result.get('response', 'Summary unavailable')
        else:
            print(f"Ollama error: {response.status_code}")
            return "Summary unavailable"
    except Exception as e:
        print(f"Error with Ollama: {e}")
        return "Ollama temporarily unavailable. Using snippet instead."


def save_to_dynamodb(research_id, topic, papers_count, summary):
    """Save to DynamoDB (25 GB free, pay per request)"""
    try:
        table.put_item(Item={
            'research_id': research_id,
            'timestamp': datetime.utcnow().isoformat(),
            'topic': topic,
            'papers_count': papers_count,
            'summary': summary,
            'status': 'completed'
        })
        print(f"Saved to DynamoDB: {research_id}")
    except Exception as e:
        print(f"DynamoDB error: {e}")


def save_to_s3(research_id, topic, papers, summary):
    """Save to S3 (5 GB free)"""
    try:
        result_data = {
            'research_id': research_id,
            'timestamp': datetime.utcnow().isoformat(),
            'topic': topic,
            'papers_found': len(papers),
            'papers': papers,
            'summary': summary
        }

        s3_client.put_object(
            Bucket=S3_BUCKET,
            Key=f"research_results/{research_id}.json",
            Body=json.dumps(result_data, indent=2),
            ContentType='application/json'
        )
        print(f"Saved to S3: {research_id}.json")
    except Exception as e:
        print(f"S3 error: {e}")


def lambda_handler(event, context):
    """Main handler - 1M requests/month FREE"""
    try:
        body = json.loads(event.get('body', '{}'))
        topic = body.get('topic', 'machine learning')
        research_id = str(uuid.uuid4())

        print(f"Starting research: {topic}")

        # Search (uses SerpAPI free tier)
        papers = search_papers(topic, num_results=3)  # Keep low to stay within free tier
        print(f"Found {len(papers)} papers")

        # Combine content
        combined_content = "\n".join([
            f"Title: {p['title']}\nSnippet: {p['snippet']}"
            for p in papers
        ])

        # Summarize (uses Ollama on EC2 - FREE)
        summary = summarize_with_ollama(combined_content, topic)

        # Save results
        save_to_dynamodb(research_id, topic, len(papers), summary)
        save_to_s3(research_id, topic, papers, summary)

        return {
            'statusCode': 200,
            'body': json.dumps({
                'research_id': research_id,
                'topic': topic,
                'papers_found': len(papers),
                'summary': summary,
                'message': 'Research completed successfully'
            })
        }

    except Exception as e:
        print(f"Error: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }