# Optional: PostgreSQL Migration Guide

If you want to upgrade from SQLite to PostgreSQL for production (recommended), follow these steps:

## 1. Update requirements.txt

Add PostgreSQL adapter to your requirements.txt:

```
Flask==2.3.3
gunicorn==21.2.0
Flask-Login==0.6.3
Flask-WTF==1.1.1
Werkzeug==2.3.7
bcrypt==4.0.1
XlsxWriter==3.1.9
psycopg2-binary==2.9.7
```

## 2. Create PostgreSQL Database on Render

1. In Render dashboard, click "New +" → "PostgreSQL"
2. Choose a name (e.g., "finance-tracker-db")
3. Select Free tier
4. Click "Create Database"
5. Copy the "External Database URL" from the database dashboard

## 3. Update Environment Variables

In your web service environment variables, add:

- `DATABASE_URL`: (paste the PostgreSQL URL from step 2)

## 4. Update db.py (Optional - for better PostgreSQL support)

Your current code already works with PostgreSQL through the DATABASE_URL environment variable!

The line `DATABASE = os.environ.get('DATABASE_URL', 'sqlite:///finance.db').replace('sqlite:///', '')`
will automatically use PostgreSQL when DATABASE_URL is set.

## 5. Deploy with PostgreSQL

1. Push changes to GitHub (if you updated requirements.txt)
2. Render will automatically redeploy
3. Your app will now use PostgreSQL instead of SQLite

## Benefits of PostgreSQL:

- Data persists between deployments
- Better performance for multiple users
- More robust for production use
- Supports concurrent connections

## Note:

Your current SQLite setup will work fine for personal use or testing. PostgreSQL is recommended for production apps with multiple users.
