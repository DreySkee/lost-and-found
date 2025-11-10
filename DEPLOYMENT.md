# Deployment Guide

This guide explains how to deploy the Lost & Found application to various hosting platforms.

## Prerequisites

- Python 3.9 or higher
- OpenAI API key (required for AI-powered item descriptions)

## Environment Variables

Create a `.env` file in the root directory (or set environment variables in your hosting platform):

```env
OPENAI_API_KEY=your_openai_api_key_here
FLASK_DEBUG=false
PORT=8080  # Usually set automatically by hosting platform
```

## OpenAI API Key

The application requires an OpenAI API key for generating item descriptions. Make sure to set the `OPENAI_API_KEY` environment variable in your hosting platform. The application will save items even without the API key, but descriptions will be limited.

## Deployment Options

### Option 1: Render

1. **Create a Render account** at https://render.com

2. **Create a new Web Service**:
   - Connect your GitHub repository
   - Select "Web Service"
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn --bind 0.0.0.0:$PORT --workers 2 --threads 2 --timeout 120 server.app:create_app`

3. **Set Environment Variables**:
   - `OPENAI_API_KEY`: Your OpenAI API key (optional)
   - `PYTHON_VERSION`: `3.11.0`

4. **Add Persistent Disk** (recommended):
   - Add a disk with at least 10GB for uploads and metadata
   - Mount path: `/opt/render/project/src`

5. **Deploy**: Render will automatically deploy your application

**Alternative**: Use the included `render.yaml` file for automatic configuration.

### Option 2: Railway

1. **Create a Railway account** at https://railway.app

2. **Create a new project**:
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository

3. **Configure**:
   - Railway will automatically detect the `railway.json` configuration
   - Add environment variables in the Railway dashboard:
     - `OPENAI_API_KEY`: Your OpenAI API key (optional)

4. **Deploy**: Railway will automatically build and deploy

### Option 3: Heroku

1. **Install Heroku CLI** and login:
   ```bash
   heroku login
   ```

2. **Create a Heroku app**:
   ```bash
   heroku create your-app-name
   ```

3. **Set environment variables**:
   ```bash
   heroku config:set OPENAI_API_KEY=your_api_key_here
   ```

4. **Deploy**:
   ```bash
   git push heroku main
   ```

5. **Add persistent storage** (recommended):
   - Heroku filesystem is ephemeral, so uploads will be lost on restart
   - Consider using Heroku Postgres or S3 for persistent storage

### Option 4: DigitalOcean App Platform

1. **Create a DigitalOcean account** at https://www.digitalocean.com

2. **Create a new App**:
   - Connect your GitHub repository
   - Select "Web Service"
   - Build Command: `pip install -r requirements.txt`
   - Run Command: `gunicorn --bind 0.0.0.0:$PORT --workers 2 --threads 2 --timeout 120 server.app:create_app`

3. **Set Environment Variables**:
   - `OPENAI_API_KEY`: Your OpenAI API key (optional)
   - `PORT`: Automatically set by DigitalOcean

4. **Add Persistent Storage** (recommended):
   - Add a volume for uploads and metadata

### Option 5: Fly.io

1. **Install Fly CLI**:
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

2. **Login and create app**:
   ```bash
   fly auth login
   fly launch
   ```

3. **Set environment variables**:
   ```bash
   fly secrets set OPENAI_API_KEY=your_api_key_here
   ```

4. **Deploy**:
   ```bash
   fly deploy
   ```

## Important Notes

### Persistent Storage

Most hosting platforms have ephemeral filesystems, meaning uploaded files and metadata will be lost when the app restarts. Consider:

1. **Using a database** for metadata (PostgreSQL, MongoDB, etc.)
2. **Using object storage** for images (AWS S3, Cloudinary, etc.)
3. **Using persistent volumes** (if supported by your hosting platform)

### Model Files

The YOLO model file (`yolov8n.pt`) is approximately 6MB. Make sure it's included in your deployment:

1. **Include in repository** (recommended for small teams)
2. **Download during build** (add to build script)
3. **Use persistent storage** and download on first run

### Performance Considerations

- The application uses OpenAI's Vision API for item descriptions
- Adjust worker and thread counts in the gunicorn command based on your server resources
- Consider rate limiting if you expect high traffic

### Security

- Never commit `.env` files or API keys to version control
- Use environment variables for all sensitive configuration
- Enable HTTPS in production (most hosting platforms provide this automatically)

## Local Development

To run locally:

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export OPENAI_API_KEY=your_api_key_here
export FLASK_DEBUG=true

# Run the application
python -m server.app
```

Or use the start script:
```bash
python -m server.app
```

The application will be available at http://localhost:8080

## Troubleshooting


### Uploads not persisting

If uploads disappear after restart:
1. Check if your hosting platform uses ephemeral storage
2. Consider using external storage (S3, etc.)
3. Implement database-backed metadata storage

### OpenAI API errors

If you see OpenAI API errors:
1. Verify your API key is set correctly
2. Check your OpenAI account has credits
3. The application will continue to work without OpenAI (descriptions will be limited)

## Support

For issues or questions, please check the main README.md or open an issue in the repository.

