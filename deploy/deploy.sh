#!/bin/bash

# Deployment Script for Django Application
# Run this script to deploy/update the application

set -e  # Exit on error

APP_DIR="/home/ubuntu/souled-backend"
VENV_DIR="$APP_DIR/venv"

echo "========================================="
echo "Starting Deployment"
echo "========================================="

# Navigate to application directory
cd $APP_DIR

# Pull latest code (if using Git)
if [ -d ".git" ]; then
    echo "Pulling latest code from Git..."
    git pull origin main
fi

# Activate virtual environment
echo "Activating virtual environment..."
source $VENV_DIR/bin/activate

# Install/update dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Run database migrations
echo "Running database migrations..."
python manage.py migrate

# Restart Gunicorn service
echo "Restarting Gunicorn..."
sudo systemctl restart gunicorn

# Restart Nginx
echo "Restarting Nginx..."
sudo systemctl restart nginx

# Check service status
echo "Checking Gunicorn status..."
sudo systemctl status gunicorn --no-pager

echo "========================================="
echo "Deployment Complete!"
echo "========================================="
echo ""
echo "Application is now running at:"
echo "https://your-domain.com"
echo ""
echo "Check logs with:"
echo "  sudo journalctl -u gunicorn -f"
echo "  sudo tail -f /var/log/nginx/souled_error.log"
