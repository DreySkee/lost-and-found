# Lost & Found Application

A web application for managing lost and found items using AI-powered item descriptions.

## Features

- 📸 **Camera Integration**: Capture photos of found items using your device's camera
- 🤖 **Smart Descriptions**: AI-generated item descriptions using OpenAI
- 📱 **Responsive Design**: Works on desktop and mobile devices
- 🔎 **Search**: Search through found items by category, color, condition, and features

## Technology Stack

- **Backend**: Flask (Python)
- **AI/ML**: OpenAI for item descriptions
- **Frontend**: HTML, CSS, JavaScript

## Prerequisites

- Python 3.9 or higher
- OpenAI API key (optional - for AI-powered item descriptions)
- Camera access (for capturing items)

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd lost-and-found
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   Create a `.env` file in the root directory:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   FLASK_DEBUG=false
   PORT=8080
   ```

5. **Run the application**:
   ```bash
   python -m server.app
   ```

   The application will be available at http://localhost:8080

## Usage

1. **Capture Items**: 
   - Navigate to `/camera` or click the camera button
   - Allow camera access when prompted
   - Take a picture of a found item
   - The system will automatically detect and describe the item

2. **Search Items**:
   - Use the search page to browse found items
   - Search by category, color, condition, or distinctive features
   - View item details and images

3. **Manage Items**:
   - View all found items on the search page
   - Delete items if no longer needed

## Deployment

See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed deployment instructions for various hosting platforms including:

- Render
- Railway
- Heroku
- DigitalOcean
- Fly.io

### Quick Deploy to Render

1. Connect your GitHub repository to Render
2. Create a new Web Service
3. Use the build command: `pip install -r requirements.txt`
4. Use the start command: `gunicorn --bind 0.0.0.0:$PORT --workers 2 --threads 2 --timeout 120 server.app:create_app`
5. Set environment variables (OPENAI_API_KEY, etc.)
6. Deploy!

## Project Structure

```
lost-and-found/
├── client/              # Frontend files
│   ├── camera.html     # Camera capture page
│   ├── search.html     # Search page
│   ├── shared.css      # Shared styles
│   └── utils.js        # Shared utilities
├── server/              # Backend application
│   ├── app.py          # Flask application
│   ├── routes/         # API routes
│   └── utils/          # Utility functions
├── requirements.txt     # Python dependencies
├── Procfile            # Heroku/Render configuration
├── render.yaml         # Render configuration
├── railway.json        # Railway configuration
└── DEPLOYMENT.md       # Deployment guide
```

## Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key (optional, for AI descriptions)
- `FLASK_DEBUG`: Set to "true" for development mode (default: false)
- `PORT`: Server port (usually set automatically by hosting platform)

## OpenAI API Key

The application uses OpenAI's Vision API to generate item descriptions. Make sure to set your `OPENAI_API_KEY` environment variable. The application will work without it, but item descriptions will be limited.

## Limitations

- Uploads are stored locally and may be lost on server restart (consider using external storage for production)
- OpenAI API key is required for item descriptions (the application will save items without descriptions if the API is unavailable)
- Camera access requires HTTPS in production (most hosting platforms provide this)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[Your License Here]

## Support

For issues or questions, please open an issue in the repository.

