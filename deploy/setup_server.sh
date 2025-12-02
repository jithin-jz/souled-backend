#!/bin/bash

# EC2 Server Setup Script for Ubuntu 22.04
# This script sets up the server for Django deployment

set -e  # Exit on error

echo "========================================="
echo "Starting EC2 Server Setup"
echo "========================================="

# Update system packages
echo "Updating system packages..."
sudo apt update
sudo apt upgrade -y

# Install Python 3.11 and pip
echo "Installing Python 3.11..."
sudo apt install -y python3.11 python3.11-venv python3-pip python3.11-dev

# Install PostgreSQL client (for Supabase connection)
echo "Installing PostgreSQL client..."
sudo apt install -y postgresql-client libpq-dev

# Install Nginx
echo "Installing Nginx..."
sudo apt install -y nginx

# Install Certbot for SSL
echo "Installing Certbot..."
sudo apt install -y certbot python3-certbot-nginx

# Install Git
echo "Installing Git..."
sudo apt install -y git

# Configure firewall
echo "Configuring UFW firewall..."
sudo ufw allow 'Nginx Full'
sudo ufw allow OpenSSH
sudo ufw --force enable

# Create swap space (important for t2.micro with 1GB RAM)
echo "Creating 2GB swap space..."
if [ ! -f /swapfile ]; then
    sudo fallocate -l 2G /swapfile
    sudo chmod 600 /swapfile
    sudo mkswap /swapfile
    sudo swapon /swapfile
    echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
fi

# Create application directory
echo "Creating application directory..."
sudo mkdir -p /home/ubuntu/souled-backend
sudo chown ubuntu:ubuntu /home/ubuntu/souled-backend

echo "========================================="
echo "Server setup complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Clone your repository to /home/ubuntu/souled-backend"
echo "2. Create and configure .env file"
echo "3. Run the deployment script"
