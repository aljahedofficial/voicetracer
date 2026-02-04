# 🚀 VoiceTracer Deployment Guide

## Quick Deploy Options

### Option 1: Streamlit Cloud (Fastest - 2 minutes)

1. **Push to GitHub**:
```bash
git add .
git commit -m "Fix: Update dependencies and tests"
git push origin main
```

2. **Deploy to Streamlit Cloud**:
- Go to [streamlit.io/cloud](https://streamlit.io/cloud)
- Click "New app"
- Select your GitHub repo
- Main file: `src/app.py`
- Click Deploy

**Result**: Live at `https://yourapp.streamlit.app` (automatic updates on git push)

---

### Option 2: Docker (Local or Server - 3 minutes)

```bash
# Build image
docker build -t voicetracer .

# Run locally
docker run -p 8501:8501 voicetracer

# Access at: http://localhost:8501
```

**Deploy to Cloud**:
- Push to Docker Hub: `docker tag voicetracer myusername/voicetracer:latest && docker push myusername/voicetracer:latest`
- Deploy to any cloud (AWS, GCP, Azure, DigitalOcean)

---

### Option 3: Traditional Server (Ubuntu/Debian)

```bash
# 1. Clone repo on server
git clone <your-repo> /opt/voicetracer

# 2. Install dependencies
cd /opt/voicetracer
pip install -e .

# 3. Create systemd service
sudo nano /etc/systemd/system/voicetracer.service
```

Paste this service file:
```ini
[Unit]
Description=VoiceTracer Streamlit Application
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/voicetracer
ExecStart=/usr/local/bin/streamlit run src/app.py --server.port=8501 --server.address=0.0.0.0
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable voicetracer
sudo systemctl start voicetracer
sudo systemctl status voicetracer
```

Setup nginx reverse proxy:
```bash
sudo nano /etc/nginx/sites-available/voicetracer
```

Paste this config:
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

Enable and reload:
```bash
sudo ln -s /etc/nginx/sites-available/voicetracer /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## Post-Deployment Checklist

- [ ] App loads without errors
- [ ] Can paste text and run analysis
- [ ] Can upload documents (TXT, DOCX, PDF)
- [ ] Metrics display correctly
- [ ] Visualizations render
- [ ] Can export to CSV/JSON
- [ ] Database auto-saves work
- [ ] Performance < 2 seconds for 5000 words

---

## Monitoring

**Streamlit Cloud**: Built-in monitoring at streamlit.io/cloud

**Docker/Server**: Check logs:
```bash
# Streamlit Cloud logs: In dashboard
# Docker logs: docker logs <container-id>
# Server logs: journalctl -u voicetracer -f
```

---

## Environment Variables (Optional)

Create `.env` file for custom config:
```
STREAMLIT_THEME_PRIMARYCOLOR=#FF6B6B
STREAMLIT_THEME_BACKGROUNDCOLOR=#FFFFFF
STREAMLIT_LOGGER_LEVEL=info
```

---

**Ready? Pick Option 1, 2, or 3 above and deploy!** 🚀
