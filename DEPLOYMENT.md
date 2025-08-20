# Render Deployment Guide

This guide will help you deploy your Personal Finance Tracker to Render.

## Prerequisites

- A GitHub account with your code pushed to a repository
- A Render account (free tier available)

## Step-by-Step Deployment

### 1. Prepare Your Repository

Make sure your code is pushed to GitHub with these files:

- ✅ `requirements.txt` - Already present
- ✅ `runtime.txt` - Specifies Python version
- ✅ `Procfile` - Tells Render how to start your app
- ✅ `app.py` - Your main Flask application

### 2. Create Render Account

1. Go to [render.com](https://render.com)
2. Sign up for a free account
3. Connect your GitHub account

### 3. Create a New Web Service

1. Click "New +" → "Web Service"
2. Connect your GitHub repository
3. Select your personal-finance-tracker repository

### 4. Configure Your Service

Fill in these settings:

- **Name**: `personal-finance-tracker` (or your preferred name)
- **Environment**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn app:app`
- **Instance Type**: `Free` (for testing)

### 5. Set Environment Variables

In the "Environment" section, add these variables:

**Required Variables:**

- `SECRET_KEY`: Generate a secure random key (use a password generator)
  Example: `your-super-secure-random-key-here-2025`
- `FLASK_ENV`: `production`

**Optional Variables:**

- `PORT`: Leave empty (Render sets this automatically)
- `RESET_DB`: Only set to `true` if you want to reset the database (DO NOT set for production!)

**⚠️ IMPORTANT DATABASE SETTING:**

- **DO NOT** set `RESET_DB=true` in production - this will delete all user data on every deployment!
- Only use `RESET_DB=true` for testing/development purposes

### 6. Deploy

1. Click "Create Web Service"
2. Render will automatically build and deploy your app
3. This process takes 2-5 minutes

### 7. Access Your App

Once deployed, you'll get a URL like:
`https://your-app-name.onrender.com`

## Database Considerations

### Current Setup (SQLite)

Your app currently uses SQLite which works but has limitations:

- Database resets on each deployment
- Not suitable for production with multiple users

### Recommended: Upgrade to PostgreSQL

For a production app, consider upgrading to PostgreSQL:

1. **Add PostgreSQL to Render:**

   - Create a new PostgreSQL database in Render (free tier available)
   - Get the database URL from Render dashboard

2. **Update your app:**
   - Add `psycopg2-binary` to requirements.txt
   - Modify database connection code to use PostgreSQL

## Troubleshooting

### Common Issues:

1. **Build fails**: Check that all dependencies are in requirements.txt
2. **App won't start**: Verify the start command is correct
3. **Database issues**: Make sure init_db() runs properly

### Logs:

- Check deployment logs in Render dashboard
- Use "Logs" tab to see runtime errors

## Post-Deployment Checklist

- [ ] App loads without errors
- [ ] User registration works
- [ ] Login/logout functionality works
- [ ] Transactions can be added/viewed
- [ ] Database persists data (if using PostgreSQL)

## Security Notes

- Never commit your SECRET_KEY to version control
- Use strong, unique SECRET_KEY for production
- Consider enabling HTTPS (automatic on Render)

## Cost

- Free tier includes:
  - 750 hours/month (enough for personal use)
  - Custom domain support
  - Automatic SSL certificates
  - Basic DDoS protection

For high-traffic apps, consider upgrading to paid tiers.
