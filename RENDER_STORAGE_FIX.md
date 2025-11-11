# Fixing Storage Issues on Render

## Problem
Render's filesystem is **ephemeral** - files are deleted on each deployment. Even with persistent disks configured, the path might not be correct.

## Solution 1: Fix Persistent Disk Configuration (Quick Fix)

### Step 1: Update Render Dashboard

1. Go to your Render dashboard
2. Select your web service
3. Go to **"Disks"** section
4. Make sure you have a disk attached with:
   - **Name**: `lost-and-found-disk`
   - **Mount Path**: `/opt/render/project/src`
   - **Size**: At least 10GB

### Step 2: Verify Disk is Mounted

The code now automatically detects if the persistent disk exists and uses it. Check your Render logs to see:
```
[INFO] Upload folder: /opt/render/project/src/uploads
[INFO] Metadata folder: /opt/render/project/src
```

### Step 3: Set Environment Variable (Optional)

You can explicitly set the persistent disk path:
- **Key**: `RENDER_PERSISTENT_DISK_PATH`
- **Value**: `/opt/render/project/src`

## Solution 2: Use Cloudinary (Recommended for Production)

Cloudinary provides reliable cloud storage that persists across deployments.

### Step 1: Sign up for Cloudinary

1. Go to https://cloudinary.com
2. Sign up for a free account
3. Get your credentials from the dashboard:
   - `CLOUDINARY_CLOUD_NAME`
   - `CLOUDINARY_API_KEY`
   - `CLOUDINARY_API_SECRET`

### Step 2: Install Cloudinary

```bash
pip install cloudinary
```

Add to `requirements.txt`:
```
cloudinary>=1.36.0
```

### Step 3: Set Environment Variables in Render

- `CLOUDINARY_CLOUD_NAME`: Your cloud name
- `CLOUDINARY_API_KEY`: Your API key
- `CLOUDINARY_API_SECRET`: Your API secret

### Step 4: Update Code (See implementation below)

The code will automatically use Cloudinary if credentials are set, otherwise fall back to local/persistent disk storage.

## Solution 3: Use AWS S3

Similar to Cloudinary but requires AWS account setup.

## Current Implementation

The code has been updated to:
1. **Automatically detect persistent disk** if available
2. **Use persistent disk** for uploads and metadata
3. **Fall back to local storage** for development

## Verifying the Fix

After deployment, check your Render logs:
1. Look for `[INFO] Upload folder:` message
2. Verify the path points to `/opt/render/project/src/uploads`
3. Upload a test image
4. Redeploy and verify the image still exists

## Important Notes

1. **Persistent disks cost money** on Render (even on free tier after usage)
2. **Cloudinary free tier** includes 25GB storage and 25GB bandwidth
3. **Metadata.json** is also stored on persistent disk
4. **Backups** are recommended for production

## Troubleshooting

### Files still disappearing?

1. Check if disk is actually mounted:
   ```bash
   # In Render shell (if available) or check logs
   ls -la /opt/render/project/src
   ```

2. Verify environment variable is set correctly

3. Check Render logs for path information

4. Consider using Cloudinary for more reliable storage

### Disk not mounting?

1. Verify disk is attached in Render dashboard
2. Check disk mount path matches `/opt/render/project/src`
3. Restart the service after attaching disk
4. Check Render documentation for disk requirements

