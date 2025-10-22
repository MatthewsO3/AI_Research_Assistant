# Autonomous Research Assistant on AWS

An AI-powered research assistant that searches the web, summarizes papers, and stores results on AWS.

## Setup

### Prerequisites
- AWS Account (free tier eligible)
- Python 3.11+
- AWS CLI configured

### Installation
```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/autonomous-research-assistant.git
cd autonomous-research-assistant

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

1. Get API keys:
   - [SerpAPI](https://serpapi.com/) - 100 searches/month free
   - [Hugging Face](https://huggingface.co/) - Free inference API

2. Set environment variables:
```bash
export SERPAPI_KEY="your_key"
export S3_BUCKET="your_bucket"
export HF_API_KEY="your_key"
```

3. Deploy to AWS Lambda (see tutorial)

## Usage
```bash
curl -X POST https://your-api.execute-api.eu-north-1.amazonaws.com/prod/research \
  -H "Content-Type: application/json" \
  -d '{"topic": "machine learning"}'
```

## Cost

**Completely FREE** - stays within AWS free tier limits:
- Lambda: 1M requests/month
- S3: 5GB storage
- DynamoDB: 25GB + 25 RCU/WCU
- SerpAPI: 100 searches/month
