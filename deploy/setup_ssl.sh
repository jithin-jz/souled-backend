#!/bin/bash

# SSL Setup Script using Let's Encrypt
# Run this after setting up your domain DNS

set -e  # Exit on error

# Configuration
DOMAIN="your-domain.com"  # Replace with your actual domain
EMAIL="your-email@example.com"  # Replace with your email

echo "========================================="
echo "Setting up SSL with Let's Encrypt"
echo "========================================="

# Check if domain is provided
if [ "$DOMAIN" = "your-domain.com" ]; then
    echo "ERROR: Please edit this script and set your actual domain name"
    exit 1
fi

# Obtain SSL certificate
echo "Obtaining SSL certificate for $DOMAIN..."
sudo certbot --nginx -d $DOMAIN -d www.$DOMAIN --non-interactive --agree-tos -m $EMAIL

# Test auto-renewal
echo "Testing certificate auto-renewal..."
sudo certbot renew --dry-run

echo "========================================="
echo "SSL Setup Complete!"
echo "========================================="
echo ""
echo "Your site is now accessible via HTTPS:"
echo "https://$DOMAIN"
echo ""
echo "Certificate will auto-renew before expiration."
echo "Check renewal status with: sudo certbot renew --dry-run"
