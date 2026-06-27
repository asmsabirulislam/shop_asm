# SoleStyle - Live Deployment Guide

## Overview
এই গাইডটি আপনার Flask-based e-commerce app (SoleStyle) কে প্রোডাকশনে লাইভ করার জন্য।

---

## ✅ Issues Fixed in app.py

1. **Removed invalid imports**: Streamlit, Pandas, Plotly (these were not being used in Flask routes)
2. **Removed header text**: "Setup (once):" and other non-Python text removed
3. **Fixed SECRET_KEY**: Now reads from environment variable with fallback
4. **Fixed DATABASE_URI**: Changed from `sqlite:///../instance/solestyle.db` to `sqlite:///solestyle.db`
5. **Added missing routes**: Checkout, Orders, Wishlist APIs properly implemented
6. **Proper Flask entrypoint**: `if __name__ == '__main__':` works correctly

---

## 🚀 Deployment Steps

### Option 1: Local Testing (Before Live)
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run Flask app locally
python app.py

# 3. Access at http://localhost:5000
```

**Test credentials:**
- Admin: `admin` / `admin`
- Demo: `demo` / `demo123`

---

### Option 2: Deploy to Render (Recommended for Quick Setup)

#### Step 1: Prepare Your Repository
```bash
git init
git add .
git commit -m "Initial commit"
git push origin main
```

#### Step 2: Create `.env` File (Don't commit this!)
```env
DATABASE_URL=postgresql://user:password@db-host/dbname
SECRET_KEY=your-secure-random-key-here
FLASK_ENV=production
```

#### Step 3: Create `runtime.txt`
```
python-3.11.0
```

#### Step 4: Create `Procfile`
```
web: gunicorn app:app
```

#### Step 5: Deploy on Render
1. Go to https://render.com
2. Click "New +" → "Web Service"
3. Connect your GitHub repo
4. Configure:
   - **Runtime**: Python 3
   - **Build command**: `pip install -r requirements.txt`
   - **Start command**: `gunicorn app:app`
5. Add Environment Variables from `.env`
6. Deploy!

---

### Option 3: Deploy to Railway

1. Go to https://railway.app
2. Click "New Project"
3. Select your GitHub repo
4. Configure environment variables
5. Railway auto-detects Flask and deploys with `gunicorn`

---

### Option 4: Deploy to Heroku (Classic)

```bash
# Install Heroku CLI
# Then:
heroku login
heroku create your-app-name
heroku config:set SECRET_KEY="your-secret-key"
heroku config:set DATABASE_URL="postgresql://..."
git push heroku main
heroku logs --tail
```

---

### Option 5: Deploy to a VPS (AWS, DigitalOcean, Linode)

#### Step 1: SSH into your server
```bash
ssh root@your-server-ip
```

#### Step 2: Install dependencies
```bash
apt update && apt upgrade -y
apt install python3 python3-pip python3-venv postgresql nginx supervisor -y
```

#### Step 3: Clone your app
```bash
cd /var/www
git clone your-repo-url solestyle
cd solestyle
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### Step 4: Create `.env` file
```bash
cat > .env << EOF
DATABASE_URL=postgresql://postgres:password@localhost/solestyle
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
FLASK_ENV=production
EOF
```

#### Step 5: Setup PostgreSQL
```bash
sudo -u postgres psql << EOF
CREATE DATABASE solestyle;
CREATE USER solestyle_user WITH PASSWORD 'strong_password';
ALTER ROLE solestyle_user SET client_encoding TO 'utf8';
ALTER ROLE solestyle_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE solestyle_user SET default_transaction_deferrable TO on;
ALTER ROLE solestyle_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE solestyle TO solestyle_user;
EOF
```

#### Step 6: Update `.env` with PostgreSQL credentials
```env
DATABASE_URL=postgresql://solestyle_user:strong_password@localhost/solestyle
```

#### Step 7: Initialize database
```bash
python3 app.py  # This will seed the DB
```

#### Step 8: Create Supervisor config (`/etc/supervisor/conf.d/solestyle.conf`)
```ini
[program:solestyle]
directory=/var/www/solestyle
command=/var/www/solestyle/venv/bin/gunicorn app:app --workers 4 --bind 127.0.0.1:5000
autostart=true
autorestart=true
stderr_logfile=/var/log/solestyle/err.log
stdout_logfile=/var/log/solestyle/out.log
environment=PATH="/var/www/solestyle/venv/bin"
user=www-data
```

#### Step 9: Setup Nginx reverse proxy
```nginx
# /etc/nginx/sites-available/solestyle
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /var/www/solestyle/static/;
    }
}
```

#### Step 10: Enable and start services
```bash
ln -s /etc/nginx/sites-available/solestyle /etc/nginx/sites-enabled/
systemctl restart nginx
supervisorctl reread
supervisorctl update
supervisorctl start solestyle
```

#### Step 11: Setup SSL with Let's Encrypt
```bash
apt install certbot python3-certbot-nginx -y
certbot --nginx -d your-domain.com
```

---

## 🗄️ Database Configuration

### SQLite (Development/Small Scale)
Already configured in `app.py` - no action needed.

### PostgreSQL (Recommended for Production)

Update `app.py` line 82:
```python
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL', 'sqlite:///solestyle.db'
)
```

Set environment variable:
```bash
export DATABASE_URL=postgresql://user:password@host:5432/solestyle
python app.py
```

---

## 📋 Pre-Deployment Checklist

- [ ] Remove debug print statements
- [ ] Set `debug=False` in app.run() ✅ (Already done)
- [ ] Use strong SECRET_KEY from environment ✅ (Already done)
- [ ] Use PostgreSQL instead of SQLite for production
- [ ] Setup CORS headers if needed (for API access from other domains)
- [ ] Add rate limiting for auth endpoints
- [ ] Setup email verification for registration
- [ ] Add SSL certificate
- [ ] Setup database backups
- [ ] Setup monitoring/logging
- [ ] Configure firewall rules

---

## 🔐 Security Best Practices

### 1. Environment Variables
```bash
# Create .env (never commit this!)
SECRET_KEY=generate-with: python3 -c "import secrets; print(secrets.token_urlsafe(32))"
DATABASE_URL=postgresql://...
FLASK_ENV=production
```

### 2. Update app.py for production
```python
# In app.py
if os.environ.get('FLASK_ENV') == 'production':
    app.config['TESTING'] = False
    app.config['PROPAGATE_EXCEPTIONS'] = True
```

### 3. Add security headers
```python
@app.after_request
def security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response
```

### 4. Setup HTTPS (redirect from HTTP)
```python
if not app.debug:
    # Force HTTPS
    @app.before_request
    def before_request():
        if not request.is_secure and os.environ.get('FLASK_ENV') == 'production':
            url = request.url.replace('http://', 'https://', 1)
            return redirect(url, code=301)
```

### 5. Rate limiting (install flask-limiter)
```bash
pip install flask-limiter
```

---

## 📊 Monitoring & Logging

### Setup Logging
```python
import logging

if not app.debug:
    handler = logging.FileHandler('solestyle.log')
    handler.setLevel(logging.WARNING)
    app.logger.addHandler(handler)
```

### Monitor Processes
- Use `pm2` or `supervisor` for process management
- Setup uptime monitoring with Uptime Robot
- Monitor disk space & database size
- Setup alerts for errors

---

## 🐛 Troubleshooting

### Port 5000 already in use
```bash
lsof -i :5000
kill -9 <PID>
```

### Database connection error
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Check connection string format:
# postgresql://username:password@localhost:5432/dbname
```

### Static files not loading
```bash
# Make sure static folder exists
mkdir -p static/images
# In production, serve static files through Nginx
```

### 502 Bad Gateway (on Nginx)
```bash
# Check Gunicorn is running
supervisorctl status solestyle

# View logs
tail -f /var/log/solestyle/err.log
```

---

## 📱 Additional Setup

### Enable Product Images
```bash
mkdir -p static/images
# Add your shoe images to static/images/
# They'll auto-sync with products on app load
```

### Seed Sample Data
```bash
python3 seed_sample_data.py
```

---

## 🎯 Next Steps After Deployment

1. **Setup SSL/HTTPS** - Essential for payment data
2. **Setup Email notifications** - Order confirmations, password resets
3. **Add payment gateway** - Stripe, Bkash (for Bangladesh)
4. **Setup analytics** - Google Analytics, Mixpanel
5. **Add backup system** - Daily DB backups
6. **Setup CDN** - CloudFlare for faster image delivery
7. **Add admin notifications** - Slack/Discord webhooks for orders

---

## ✨ Test Your Deployment

```bash
# Check app is running
curl http://your-domain.com

# Login and test orders
# Visit /admin to check dashboard
# Check sample data is loaded
```

---

## 🆘 Quick Support Commands

```bash
# View Nginx logs
tail -f /var/log/nginx/error.log

# View app logs
tail -f /var/log/solestyle/err.log

# Restart app
supervisorctl restart solestyle

# Check disk space
df -h

# Check database size
psql -d solestyle -c "SELECT pg_size_pretty(pg_database_size('solestyle'));"
```

---

**আপনার app এখন production-ready! Good luck! 🚀**
