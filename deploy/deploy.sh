#!/bin/bash

set -e

echo "🚀 Starting deployment..."

# Variables
PROJECT_DIR="/var/www/habits-tracker"
USER="www-data"
GROUP="www-data"

echo "📁 Moving to project directory..."
cd $PROJECT_DIR

echo "📦 Pulling latest changes..."
git pull origin main

echo "🐍 Activating virtual environment..."
source venv/bin/activate

echo "📋 Installing dependencies..."
pip install -r requirements.txt

echo "🗄️ Running migrations..."
python manage.py migrate

echo "🗄️ Collecting static files..."
python manage.py collectstatic --noinput

echo "🔄 Restarting Gunicorn..."
sudo systemctl restart gunicorn

echo "🔄 Reloading Nginx..."
sudo systemctl reload nginx

echo "✅ Deployment complete!"