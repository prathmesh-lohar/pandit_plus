#!/bin/bash

set -e

# ----------------------------
# Configuration — edit these
# ----------------------------
APP_NAME="pandit_plus"
REPO_URL="https://github.com/prathmesh-lohar/pandit_plus.git"
DOMAIN="13.60.31.100"          # Replace with your domain or EC2 public IP
APP_DIR="/var/www/html/$APP_NAME"
USER="www-data"
PYTHON_BIN="python3"
VENV_DIR="$APP_DIR/venv"

# ----------------------------
# Update & install required packages
# ----------------------------
echo "🚀 Updating system..."
sudo apt update && sudo apt upgrade -y

echo "📦 Installing dependencies..."
sudo apt install -y python3-pip python3-venv python3-dev libpq-dev nginx git curl

# ----------------------------
# Clone repo 
# ----------------------------
if [ -d "$APP_DIR" ]; then
    echo "📂 Directory $APP_DIR already exists — pulling latest changes"
    cd $APP_DIR
    sudo -u $USER git pull
else
    echo "📂 Cloning project into $APP_DIR"
    sudo git clone $REPO_URL $APP_DIR
    sudo chown -R $USER:$USER $APP_DIR
fi

cd $APP_DIR

# ----------------------------
# Setup virtual environment
# ----------------------------
if [ ! -d "$VENV_DIR" ]; then
    echo "🐍 Creating virtual environment..."
    sudo -u $USER $PYTHON_BIN -m venv venv
fi

echo "📥 Activating venv and installing requirements..."
# run pip install as the USER, not root
sudo -u $USER bash -c "source $VENV_DIR/bin/activate && pip install --upgrade pip && pip install -r requirements.txt"

# ----------------------------
# Django setup: migrations + collectstatic
# ----------------------------
echo "✳️ Running migrations..."
sudo -u $USER bash -c "source $VENV_DIR/bin/activate && cd $APP_DIR && $PYTHON_BIN manage.py migrate"

echo "🧹 Collecting static files..."
sudo -u $USER bash -c "source $VENV_DIR/bin/activate && cd $APP_DIR && $PYTHON_BIN manage.py collectstatic --noinput"

# ----------------------------
# Gunicorn systemd service
# ----------------------------
echo "📝 Setting up systemd service for Gunicorn..."
SERVICE_FILE="/etc/systemd/system/gunicorn_$APP_NAME.service"

sudo tee $SERVICE_FILE > /dev/null <<EOL
[Unit]
Description=gunicorn daemon for $APP_NAME
After=network.target

[Service]
User=$USER
Group=$USER
WorkingDirectory=$APP_DIR
ExecStart=$APP_DIR/venv/bin/gunicorn --workers 3 --bind unix:$APP_DIR/gunicorn.sock $APP_NAME.wsgi:application

Restart=always

[Install]
WantedBy=multi-user.target
EOL

echo "🔄 Starting and enabling Gunicorn service..."
sudo systemctl daemon-reload
sudo systemctl enable --now gunicorn_$APP_NAME.service

# ----------------------------
# Nginx configuration
# ----------------------------
echo "🌐 Configuring Nginx..."
NGINX_CONF="/etc/nginx/sites-available/$APP_NAME"

sudo tee $NGINX_CONF > /dev/null <<EOL
server {
    listen 80;
    server_name $DOMAIN;

    location = /favicon.ico { access_log off; log_not_found off; }
    location /static/ {
        alias $APP_DIR/static/;
    }

    location /media/ {
        alias $APP_DIR/media/;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:$APP_DIR/gunicorn.sock;
    }
}
EOL

sudo ln -sf $NGINX_CONF /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# ----------------------------
# Permissions
# ----------------------------
echo "🔐 Setting proper permissions..."
sudo chown -R $USER:$USER $APP_DIR
sudo chmod -R 755 $APP_DIR

echo "✅ Deployment done! Visit: http://$DOMAIN"


