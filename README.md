# 🧠 AI Research Assistant

> **Your personal research assistant**

This AI-powered assitant searches, summarizes, and stores research findings.

## 🎯 What Does This Thing Do?

Think of it as your overachieving research intern who:
- 🔍 **Searches the web**
- 📚 **Summarizes complex papers**
- ☁️ **Stores everything on AWS** 
- 🤖 **Runs autonomously** 

## ✨ Features

- **Completely FREE** - Stays comfortably within AWS free tier limits (because broke researchers are still researchers)
- **Serverless Architecture** - No servers to maintain, no DevOps nightmares
- **Smart Summarization** - Powered by Hugging Face's inference API
- **Web Search Integration** - Uses SerpAPI to find the juiciest academic content
- **Cloud Storage** - All your research findings safely tucked away in S3

## 🚀 Quick Start

### Prerequisites

You'll need:
- An AWS Account
- Python 3.11 or higher
- AWS CLI configured on your machine

### Installation

```bash
# Clone this bad boy
git clone https://github.com/MatthewsO3/AI_Research_Assistant.git
cd AI_Research_Assistant

# Set up your Python playground
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the magic
pip install -r requirements.txt
```

### Get Your API Keys

You'll need two free API keys

1. **SerpAPI** - [Sign up here](https://serpapi.com/)
   - Free tier: 100 searches/month 
   
2. **Hugging Face** - [Sign up here](https://huggingface.co/)
   - Free inference API (unlimited for most models)

### Configure Environment

```bash
export SERPAPI_KEY="your_serpapi_key_here"
export S3_BUCKET="your_unique_bucket_name"
export HF_API_KEY="your_huggingface_key_here"
```

Pro tip: Add these to your `.bashrc` or `.zshrc` so you don't have to set them every time.

## 🎮 Usage

### Local Testing

```bash
# Run the assistant locally
python lambda_function.py
```

### Deployed to AWS Lambda

Once deployed (see deployment guide below), hit your API:

```bash
curl -X POST https://your-api.execute-api.eu-north-1.amazonaws.com/prod/research \
  -H "Content-Type: application/json" \
  -d '{"topic": "quantum computing applications"}'
```

The assistant will:
1. Search for relevant papers on your topic
2. Fetch and analyze the content
3. Generate concise summaries
4. Store everything in your S3 bucket
5. Return a JSON response with all papers

## 📦 What's Inside?

```
AI_Research_Assistant/
├── lambda_function.py   
├── requirements.txt      
└── README.md           
```

## 💰 Cost Breakdown

- **AWS Lambda**: 1M requests/month free 
- **S3 Storage**: 5GB free 
- **DynamoDB**: 25GB storage + 25 read/write units free
- **SerpAPI**: 100 searches/month free tier
- **Hugging Face**: Free inference API


## 🛠️ Deployment to AWS Lambda

Detailed deployment guide coming soon! In the meantime:

1. Package your code with dependencies
2. Create a Lambda function with Python 3.11 runtime
3. Set up API Gateway trigger
4. Configure environment variables
5. Deploy and test

## Example
<img width="1715" height="811" alt="Screenshot 2025-10-24 at 12 07 33" src="https://github.com/user-attachments/assets/317ac728-abc2-47ab-b6bb-10fe3765e26a" />



