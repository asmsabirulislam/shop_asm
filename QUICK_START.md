# SoleStyle - Quick Start Guide

## 🚀 Local Development (Windows/Mac/Linux)

### 1. Install Python
- Download Python 3.10+ from https://python.org
- Make sure to check "Add Python to PATH"

### 2. Setup Project
```bash
# Clone or download your project
cd solestyle

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Run the App
```bash
python app.py
```

Open browser: **http://localhost:5000**

### 4. Test Accounts
- **Admin**: username: `admin` password: `admin`
- **Demo**: username: `demo` password: `demo123`

---

## 🌐 Deploy to Live (Step-by-Step)

### Option A: Render.com (Easiest - Free Tier Available)

**Step 1:** Push code to GitHub
```bash
git init
git add .
git commit -m "Initial commit"
git push -u origin main
```

**Step 2:** Go to https://render.com and sign up

**Step 3:** Create `.env` file locally (don't commit)
```
SECRET_KEY=any-random-string-here
DATABASE_URL=sqlite:///solestyle.db
```

**Step 4:** Click "New +" → "Web Service"
- Connect your GitHub repo
- Name: `solestyle`
- Runtime: `Python 3`
- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn app:app`

**Step 5:** Add environment variables in Render dashboard
- `SECRET_KEY`: Your secret key
- `DATABASE_URL`: `sqlite:///solestyle.db` (or PostgreSQL URL)

**Step 6:** Deploy!
- Click Deploy
- Wait ~2-3 minutes
- Your app is LIVE! 🎉

---

### Option B: Railway.app (Very Easy)

**Step 1:** Go to https://railway.app

**Step 2:** Click "New Project" → "Deploy from GitHub"

**Step 3:** Select your repository

**Step 4:** Railway auto-detects Flask
- Automatically installs dependencies
- Sets up environment variables in dashboard
- Deploys with gunicorn

**Step 5:** Set your domain and you're done! ✅

---

### Option C: Heroku (Still Possible, Now Paid)

```bash
# Install Heroku CLI from https://devcenter.heroku.com/articles/heroku-cli

heroku login
heroku create your-app-name
git push heroku main

# Set environment variables
heroku config:set SECRET_KEY="your-secret"
heroku config:set DATABASE_URL="postgresql://..."

# View logs
heroku logs --tail
```

---

### Option D: DigitalOcean ($6-12/month)

1. Create Ubuntu droplet
2. SSH into server
3. Run these commands:

```bash
apt update && apt upgrade -y
apt install python3-pip python3-venv git nginx supervisor -y

cd /var/www
git clone your-repo-url solestyle
cd solestyle
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create .env
nano .env
# Add:
# DATABASE_URL=sqlite:///solestyle.db
# SECRET_KEY=your-secret-key

# Test run
python3 app.py
# If it works, press Ctrl+C to stop

# Setup supervisor for auto-restart
sudo nano /etc/supervisor/conf.d/solestyle.conf
```

Copy this into the file:
```ini
[program:solestyle]
directory=/var/www/solestyle
command=/var/www/solestyle/venv/bin/gunicorn app:app --bind 127.0.0.1:5000
autostart=true
autorestart=true
user=www-data
```

Then:
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start solestyle
```

Setup Nginx:
```bash
sudo nano /etc/nginx/sites-available/solestyle
```

Paste:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static/ {
        alias /var/www/solestyle/static/;
    }
}
```

Enable and restart:
```bash
sudo ln -s /etc/nginx/sites-available/solestyle /etc/nginx/sites-enabled/
sudo systemctl restart nginx
```

Get SSL (free):
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

---

## ✅ Verify Deployment Works

After deploying, test these:

1. **Homepage loads**: https://your-domain.com
2. **Can register**: Create new account
3. **Can login**: Use test account
4. **Admin panel**: https://your-domain.com/admin (login as admin)
5. **Database seeded**: See products on homepage

---

## 🔍 Troubleshooting Deployment

### "502 Bad Gateway"
- App crashed. Check logs on your platform's dashboard
- Make sure all dependencies in `requirements.txt` are installed

### "Database error"
- For SQLite: Data will be stored on server's disk (temporary)
- For production: Use PostgreSQL (add DATABASE_URL env var)

### "Static files not loading"
- Make sure `static/` folder exists
- Deploy from root directory of your project

### Port already in use
```bash
# Find what's using port 5000
lsof -i :5000
# Kill it
kill -9 <PID>
```

---

## 📱 Next Steps

✅ **Deployment done!**

Now:
1. Add your domain to Nginx/Render settings
2. Setup SSL certificate (free with Let's Encrypt)
3. Add product images to `static/images/`
4. Seed sample data: `python3 seed_sample_data.py`
5. Configure payment gateway (Stripe, Bkash)
6. Setup email notifications
7. Add analytics

---

## 🆘 Need Help?

- **Render support**: https://render.com/docs
- **Flask docs**: https://flask.palletsprojects.com
- **Python virtual env**: https://docs.python.org/3/tutorial/venv.html

---

**Your store is LIVE! 🎉 Start selling!**
