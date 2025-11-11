# Quick Deployment Guide

## 🚀 Recommended: Render (Easiest)

### Step 1: Push to GitHub
```bash
# If you haven't already, initialize git and push to GitHub
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin <your-github-repo-url>
git push -u origin main
```

### Step 2: Deploy to Render

1. **Sign up** at https://render.com (free account)

2. **Create New Web Service**:
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select your repository

3. **Configure** (Render will auto-detect from `render.yaml`):
   - **Name**: `lost-and-found` (or any name you want)
   - **Region**: Choose closest to you
   - **Branch**: `main`
   - **Root Directory**: Leave empty (or `.` if needed)
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT --workers 2 --threads 2 --timeout 120 wsgi:app`

4. **Add Environment Variables**:
   - Click "Advanced" → "Add Environment Variable"
   - Key: `OPENAI_API_KEY`
   - Value: Your OpenAI API key (get it from https://platform.openai.com/api-keys)

5. **Deploy**:
   - Click "Create Web Service"
   - Wait for build to complete (5-10 minutes)
   - Your app will be live at `https://your-app-name.onrender.com`

### Step 3: Test Your Deployment
- Visit your app URL
- Test the camera feature
- Upload an item
- Check that it appears in search

---

## 🚂 Alternative: Railway (Also Easy)

### Step 1: Push to GitHub (same as above)

### Step 2: Deploy to Railway

1. **Sign up** at https://railway.app (free account with GitHub)

2. **Create New Project**:
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository

3. **Add Environment Variable**:
   - Click on your service
   - Go to "Variables" tab
   - Add: `OPENAI_API_KEY` = your API key

4. **Deploy**:
   - Railway auto-detects `railway.json`
   - Builds and deploys automatically
   - Your app will be live at `https://your-app-name.up.railway.app`

---

## 🐳 Alternative: Fly.io

### Step 1: Install Fly CLI
```bash
curl -L https://fly.io/install.sh | sh
```

### Step 2: Login and Deploy
```bash
fly auth login
fly launch
# Follow the prompts
fly secrets set OPENAI_API_KEY=your_api_key_here
fly deploy
```

---

## 📝 Important Notes

### Environment Variables
Make sure to set:
- `OPENAI_API_KEY`: Required for item descriptions
- `PORT`: Usually set automatically by the platform
- `FLASK_DEBUG`: Set to `false` for production

### Storage Warning
⚠️ **Important**: Most free tiers have **ephemeral storage**, meaning uploads will be lost when the app restarts or redeploys!

**Solutions**:
1. **Use External Storage**:
   - AWS S3 (recommended for production)
   - Cloudinary (easy setup, free tier available)
   - Google Cloud Storage
2. **Use Database** for metadata (PostgreSQL, MongoDB)
3. **Use Persistent Volumes** (if supported by your hosting platform)

### HTTPS
All platforms provide HTTPS automatically, which is required for camera access in browsers.

### Free Tier Limitations
- **Render**: Free tier sleeps after 15 minutes of inactivity
- **Railway**: Limited free credits per month
- **Fly.io**: Free tier available with limits

---

## 🔧 Troubleshooting

### App won't start
- Check build logs for errors
- Verify all dependencies in `requirements.txt`
- Check that `wsgi.py` exists

### Uploads not saving
- Check if persistent disk is mounted
- Verify uploads folder permissions
- Consider using external storage

### Camera not working
- Verify HTTPS is enabled (should be automatic)
- Check browser console for errors
- Test on different browsers/devices

### OpenAI errors
- Verify API key is set correctly
- Check OpenAI account has credits
- App will work without OpenAI but with limited functionality

---

## 🎯 Next Steps After Deployment

1. **Set up custom domain** (optional)
2. **Monitor logs** for errors
3. **Set up backups** for metadata
4. **Configure external storage** for uploads (recommended)
5. **Set up monitoring** (optional)

---

## 📚 More Details

See `DEPLOYMENT.md` for detailed instructions for all platforms.

