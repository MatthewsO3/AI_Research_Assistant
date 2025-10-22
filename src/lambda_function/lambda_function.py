import json
import boto3
import requests
import uuid
from datetime import datetime
import os

# AWS clients
s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('ResearchResults')

# Configuration from environment
SERPAPI_KEY = os.environ['SERPAPI_KEY']
S3_BUCKET = os.environ['S3_BUCKET']


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


def summarize_with_llm(content, topic):
    """Use Hugging Face BART model for summarization"""
    try:
        print(f"Starting BART summarization for topic: {topic}")
        api_url = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
        headers = {"Authorization": f"Bearer {os.environ['HF_API_KEY']}"}

        prompt = content[:1000]
        print(f"Sending to BART: {len(prompt)} chars")

        response = requests.post(
            api_url,
            headers=headers,
            json={
                "inputs": prompt,
                "parameters": {
                    "max_length": 150,
                    "min_length": 50
                }
            },
            timeout=120
        )

        print(f"BART response status: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print(f"BART result: {result}")
            if isinstance(result, list) and len(result) > 0:
                summary = result[0].get('summary_text', 'Summary unavailable')
                print(f"Extracted summary: {summary}")
                return summary
            return str(result)
        else:
            print(f"HF API Error: {response.status_code} - {response.text}")
            return "Summary unavailable"
    except Exception as e:
        print(f"Error in BART: {e}")
        import traceback
        traceback.print_exc()
        return "Summary unavailable"
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
        papers = search_papers(topic, num_results=3)
        print(f"Found {len(papers)} papers")

        # Combine content
        combined_content = "\n".join([
            f"Title: {p['title']}\nSnippet: {p['snippet']}"
            for p in papers
        ])

        # Summarize (uses HF BART)
        summary = summarize_with_llm(combined_content, topic)

        # Save results
        save_to_dynamodb(research_id, topic, len(papers), summary)
        save_to_s3(research_id, topic, papers, summary)

        return {
            'statusCode': 200,
            'body': json.dumps({
                'research_id': research_id,
                'topic': topic,
                'papers_found': len(papers),
                'papers': papers,  # ADD THIS LINE
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