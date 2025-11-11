# Deployment Checklist

## Pre-Deployment

- [ ] Review and update `README.md` with your repository URL
- [ ] Set up OpenAI API key (optional but recommended)
- [ ] Test the application locally
- [ ] Verify all dependencies are in `requirements.txt`
- [ ] Ensure `.env` is in `.gitignore` (it should be)

## Choose Your Hosting Platform

### Option 1: Render (Recommended for beginners)

1. [ ] Create account at https://render.com
2. [ ] Create new Web Service
3. [ ] Connect GitHub repository
4. [ ] Set build command: `pip install -r requirements.txt`
5. [ ] Set start command: `gunicorn --bind 0.0.0.0:$PORT --workers 2 --threads 2 --timeout 120 wsgi:app`
6. [ ] Add environment variable: `OPENAI_API_KEY` (your API key)
7. [ ] Deploy!

### Option 2: Railway

1. [ ] Create account at https://railway.app
2. [ ] Create new project from GitHub
3. [ ] Add environment variable: `OPENAI_API_KEY`
4. [ ] Railway will auto-detect `railway.json` configuration
5. [ ] Deploy!

### Option 3: Heroku

1. [ ] Install Heroku CLI
2. [ ] Run `heroku login`
3. [ ] Run `heroku create your-app-name`
4. [ ] Run `heroku config:set OPENAI_API_KEY=your_key`
5. [ ] Run `git push heroku main`
6. [ ] Note: Heroku has ephemeral storage - consider using external storage

### Option 4: DigitalOcean App Platform

1. [ ] Create account at https://digitalocean.com
2. [ ] Create new App from GitHub
3. [ ] Set build command: `pip install -r requirements.txt`
4. [ ] Set run command: `gunicorn --bind 0.0.0.0:$PORT --workers 2 --threads 2 --timeout 120 wsgi:app`
5. [ ] Add environment variables
6. [ ] Add persistent volume for uploads
7. [ ] Deploy!

## Post-Deployment

- [ ] Test the application at your deployed URL
- [ ] Verify camera functionality works (requires HTTPS)
- [ ] Test image upload and detection
- [ ] Verify OpenAI integration (if configured)
- [ ] Check that uploads persist (if using persistent storage)
- [ ] Monitor logs for any errors
- [ ] Set up custom domain (optional)
- [ ] Configure HTTPS (usually automatic on most platforms)

## Environment Variables to Set

- `OPENAI_API_KEY`: Your OpenAI API key (optional)
- `FLASK_DEBUG`: Set to "false" for production
- `PORT`: Usually set automatically by hosting platform

## Important Notes

1. **Storage**: Most platforms have ephemeral storage - uploads may be lost on restart or redeploy. Consider:
   - Using external storage (S3, Cloudinary)
   - Using a database for metadata
2. **HTTPS**: Required for camera access in browsers
3. **Performance**: Adjust worker/thread counts based on resources
4. **OpenAI API**: Required for item descriptions (application will work without it but with limited functionality)

## Troubleshooting


### Uploads not persisting
- Check if your hosting platform uses ephemeral storage
- Consider using external storage (S3, Cloudinary, etc.)
- Use a database for metadata persistence

### Camera not working
- Verify HTTPS is enabled
- Check browser permissions
- Test on different devices

### OpenAI API errors
- Verify API key is set correctly
- Check API account has credits
- Application will work without OpenAI (limited descriptions)

## Support

For issues, check:
1. Application logs in hosting platform dashboard
2. `DEPLOYMENT.md` for detailed instructions
3. GitHub issues (if applicable)

