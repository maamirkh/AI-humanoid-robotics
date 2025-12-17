# Deploying RAG Chatbot Backend to Hugging Face Spaces

This guide explains how to deploy your FastAPI-based RAG Chatbot Backend to Hugging Face Spaces.

## Prerequisites

1. Hugging Face account (https://huggingface.co)
2. Your API token from Hugging Face (Settings > Access Tokens)
3. All required API keys for external services:
   - Cohere API key
   - Qdrant Cloud API key and URL
   - Google Gemini API key
   - Neon PostgreSQL connection string

## Step-by-Step Deployment Instructions

### Step 1: Prepare Your Repository

1. Ensure all necessary files are in your backend directory:
   - `app.py` (entry point for Hugging Face Spaces)
   - `Dockerfile`
   - `requirements.txt`
   - `src/` directory with your application code
   - `README.md`
   - Any other supporting files

2. The repository should have the following structure:
```
backend/
├── app.py                 # Entry point (created for Hugging Face)
├── Dockerfile             # Container configuration
├── requirements.txt       # Python dependencies
├── src/                   # Your FastAPI application
│   ├── main.py
│   ├── api/
│   ├── core/
│   ├── models/
│   └── services/
├── README.md
└── SPACE_README.md        # Hugging Face specific documentation
```

### Step 2: Create a New Hugging Face Space

1. Go to https://huggingface.co/spaces
2. Click "Create new Space"
3. Fill in the details:
   - Name: Choose a unique name for your space
   - License: MIT or your preferred license
   - SDK: Select "Docker" (since we have a custom Dockerfile)
   - Hardware: CPU (or GPU if needed)
   - Visibility: Public or Private

### Step 3: Upload Your Code

#### Option A: Direct Upload (Simple)

1. After creating the Space, you'll see a Git repository URL
2. Clone the Space repository:
   ```bash
   git clone https://huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE_NAME
   cd YOUR_SPACE_NAME
   ```

3. Copy all your backend files to this directory:
   ```bash
   # From your project's backend directory
   cp app.py Dockerfile requirements.txt README.md SPACE_README.md ../YOUR_SPACE_NAME/

   # Copy the entire src directory
   cp -r src ../YOUR_SPACE_NAME/

   # Copy any other necessary files
   ```

4. Commit and push:
   ```bash
   git add .
   git commit -m "Initial deployment of RAG Chatbot Backend"
   git push origin main
   ```

#### Option B: Link to Existing Git Repository

1. In your Space settings, you can link to your existing GitHub repository
2. This keeps your Space synchronized with your GitHub repo

### Step 4: Configure Environment Variables

1. Go to your Space settings
2. Navigate to "Secrets" section
3. Add the following environment variables as secrets:

```
COHERE_API_KEY = your_cohere_api_key
QDRANT_API_KEY = your_qdrant_api_key
QDRANT_URL = your_qdrant_cloud_url
DATABASE_URL = your_neon_postgres_connection_string
GEMINI_API_KEY = your_gemini_api_key
```

⚠️ **Important**: Never commit these secrets to your repository. Always add them as Space secrets.

### Step 5: Monitor the Deployment

1. Watch the build logs in your Space page
2. The Space will build using your Dockerfile
3. Once built, it will start the application
4. The application will be available at: `https://YOUR_USERNAME-YOUR_SPACE_NAME.hf.space`

### Step 6: Verify the Deployment

1. Visit your Space URL
2. Check the API documentation at `/api/v1/docs`
3. Test the health endpoint at `/api/v1/health/`
4. Verify that all required environment variables are properly loaded

## Troubleshooting

### Common Issues:

1. **Build Failures**: Check the build logs for dependency installation issues
2. **Runtime Errors**: Look at the runtime logs for configuration problems
3. **Port Issues**: Ensure your application binds to the PORT environment variable (default: 7860)
4. **Environment Variables**: Verify all required secrets are set correctly

### Port Configuration:

Your application should use the `PORT` environment variable:
```python
import os
port = int(os.environ.get("PORT", 7860))
```

### Dockerfile Notes:

The Dockerfile provided handles:
- Python 3.11 environment
- Dependency installation
- Proper port exposure
- Application startup

## Scaling Considerations

- Hugging Face Spaces have resource limitations (CPU/RAM)
- For production use, consider a dedicated cloud provider
- Vector database operations might be slower on limited resources
- Plan for API rate limits from external services

## Security Best Practices

- Never store API keys in the repository
- Use Space secrets for all sensitive data
- Limit access to your Space if needed
- Regularly rotate API keys

## Updating Your Deployment

To update your Space after the initial deployment:
1. Make changes to your local code
2. Commit and push to the Space repository
3. The Space will rebuild and redeploy automatically

## Testing the API

Once deployed, you can test your API endpoints:
- Health check: `https://YOUR_USERNAME-YOUR_SPACE_NAME.hf.space/api/v1/health/`
- API Docs: `https://YOUR_USERNAME-YOUR_SPACE_NAME.hf.space/api/v1/docs`
- Chat endpoint: `https://YOUR_USERNAME-YOUR_SPACE_NAME.hf.space/api/v1/chat/`

Remember to update your frontend (Docusaurus textbook) to point to your deployed backend URL.