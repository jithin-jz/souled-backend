# AWS EC2 Free Tier Deployment Guide

Complete guide to deploy Django backend on AWS EC2 (t2.micro) with Supabase PostgreSQL.

## Architecture

- **AWS EC2**: t2.micro (1 vCPU, 1GB RAM) - Free Tier
- **Supabase**: PostgreSQL database - Free Tier (500MB)
- **Nginx**: Reverse proxy + SSL termination
- **Gunicorn**: WSGI application server
- **Cloudinary**: Media storage (already configured)
- **Stripe**: Payment processing (already configured)
- **Let's Encrypt**: Free SSL certificates

**Total Cost**: $0/month (within free tier limits)

---

## Prerequisites

### 1. AWS Account

- Must be within first 12 months for EC2 free tier
- Valid credit card required

### 2. Supabase Account

- Sign up at [supabase.com](https://supabase.com)
- Free tier: 500MB database, 2GB bandwidth

### 3. Domain Name (Optional but Recommended)

- For custom domain and SSL certificate
- Can use Namecheap, GoDaddy, or Cloudflare

---

## Part 1: Supabase Setup

### Step 1: Create Supabase Project

1. Go to [supabase.com](https://supabase.com) and sign in
2. Click "New Project"
3. Fill in details:
   - **Name**: souled-db
   - **Database Password**: Create a strong password (save this!)
   - **Region**: Choose closest to your users
4. Click "Create new project"
5. Wait 2-3 minutes for setup

### Step 2: Get Database Connection String

1. In Supabase Dashboard, go to **Project Settings** (gear icon)
2. Click **Database** in sidebar
3. Scroll to **Connection String**
4. Select **URI** tab
5. Copy the connection string:
   ```
   postgresql://postgres:[YOUR-PASSWORD]@db.xxxxxxxxxxxxx.supabase.co:5432/postgres
   ```
6. Replace `[YOUR-PASSWORD]` with your actual database password
7. **Save this** - you'll need it for `.env` file

---

## Part 2: AWS EC2 Setup

### Step 1: Launch EC2 Instance

1. **Sign in to AWS Console**: [console.aws.amazon.com](https://console.aws.amazon.com)

2. **Navigate to EC2**:

   - Search for "EC2" in services
   - Click "Launch Instance"

3. **Configure Instance**:

   **Name**: `souled-backend`

   **Application and OS Images**:

   - **AMI**: Ubuntu Server 22.04 LTS (Free tier eligible)

   **Instance Type**:

   - **Type**: t2.micro (Free tier eligible)
   - 1 vCPU, 1 GiB RAM

   **Key Pair**:

   - Click "Create new key pair"
   - **Name**: `souled-backend-key`
   - **Type**: RSA
   - **Format**: `.pem` (for Mac/Linux) or `.ppk` (for Windows/PuTTY)
   - Download and **save securely**

   **Network Settings**:

   - Click "Edit"
   - **Auto-assign public IP**: Enable
   - **Firewall (security groups)**: Create new
     - **Security group name**: `souled-backend-sg`
     - **Description**: Security group for Django backend

   **Add Security Group Rules**:

   - **SSH** (Port 22): My IP (for your IP only)
   - **HTTP** (Port 80): Anywhere (0.0.0.0/0)
   - **HTTPS** (Port 443): Anywhere (0.0.0.0/0)

   **Storage**:

   - **Size**: 8 GiB (Free tier: up to 30 GiB)
   - **Type**: gp3

4. **Launch Instance**

   - Review settings
   - Click "Launch instance"
   - Wait 1-2 minutes for instance to start

5. **Get Public IP**:
   - Go to EC2 Dashboard → Instances
   - Select your instance
   - Copy **Public IPv4 address** (e.g., `54.123.45.67`)
   - **Save this** - you'll need it

### Step 2: Allocate Elastic IP (Optional but Recommended)

This gives you a permanent IP address that won't change if you restart the instance.

1. EC2 Dashboard → **Elastic IPs** (left sidebar)
2. Click "Allocate Elastic IP address"
3. Click "Allocate"
4. Select the new IP → **Actions** → **Associate Elastic IP address**
5. Select your instance → Click "Associate"
6. **Save the new Elastic IP** - use this instead of the public IP

---

## Part 3: Server Setup

### Step 1: Connect to EC2 Instance

**On Mac/Linux**:

```bash
# Set key permissions
chmod 400 souled-backend-key.pem

# Connect via SSH
ssh -i souled-backend-key.pem ubuntu@YOUR-EC2-PUBLIC-IP
```

**On Windows** (using PuTTY):

1. Open PuTTY
2. Host Name: `ubuntu@YOUR-EC2-PUBLIC-IP`
3. Connection → SSH → Auth → Browse for your `.ppk` key
4. Click "Open"

### Step 2: Run Server Setup Script

```bash
# Download setup script
wget https://raw.githubusercontent.com/YOUR-USERNAME/YOUR-REPO/main/deploy/setup_server.sh

# Make executable
chmod +x setup_server.sh

# Run setup
./setup_server.sh
```

**Or manually**:

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.11
sudo apt install -y python3.11 python3.11-venv python3-pip python3.11-dev

# Install PostgreSQL client
sudo apt install -y postgresql-client libpq-dev

# Install Nginx
sudo apt install -y nginx

# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Install Git
sudo apt install -y git

# Configure firewall
sudo ufw allow 'Nginx Full'
sudo ufw allow OpenSSH
sudo ufw --force enable

# Create swap (important for 1GB RAM)
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

---

## Part 4: Application Deployment

### Step 1: Clone Repository

```bash
# Navigate to home directory
cd /home/ubuntu

# Clone your repository
git clone https://github.com/YOUR-USERNAME/YOUR-REPO.git souled-backend
cd souled-backend
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python3.11 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables

```bash
# Create .env file
nano .env
```

**Add the following** (replace with your actual values):

```env
SECRET_KEY=your-django-secret-key-generate-new-one
DEBUG=False
ALLOWED_HOSTS=YOUR-EC2-IP,your-domain.com

DATABASE_URL=postgresql://postgres:YOUR-PASSWORD@db.xxxxx.supabase.co:5432/postgres

CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret

STRIPE_SECRET_KEY=sk_live_your-stripe-key
STRIPE_WEBHOOK_SECRET=whsec_your-webhook-secret

GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com

FRONTEND_URL=https://your-frontend.vercel.app

CORS_ALLOWED_ORIGINS=https://your-frontend.vercel.app
CSRF_TRUSTED_ORIGINS=https://your-frontend.vercel.app

SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

**Generate SECRET_KEY**:

```bash
python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

Save and exit: `Ctrl+X`, then `Y`, then `Enter`

### Step 4: Run Migrations

```bash
# Activate virtual environment if not already
source venv/bin/activate

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput
```

### Step 5: Test Gunicorn

```bash
# Test Gunicorn
gunicorn --config gunicorn_config.py store.wsgi:application
```

Press `Ctrl+C` to stop. If it works, proceed to next step.

---

## Part 5: Configure Systemd Service

### Step 1: Create Gunicorn Service

```bash
# Copy service file
sudo cp deploy/gunicorn.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Start Gunicorn
sudo systemctl start gunicorn

# Enable auto-start on boot
sudo systemctl enable gunicorn

# Check status
sudo systemctl status gunicorn
```

**Troubleshooting**:

```bash
# View logs
sudo journalctl -u gunicorn -f

# Restart service
sudo systemctl restart gunicorn
```

---

## Part 6: Configure Nginx

### Step 1: Update Nginx Configuration

```bash
# Edit nginx config
sudo nano deploy/nginx.conf
```

**Replace**:

- `your-domain.com` with your actual domain (or EC2 IP for testing)
- `/home/ubuntu/souled-backend` with your actual path

### Step 2: Install Nginx Configuration

```bash
# Remove default config
sudo rm /etc/nginx/sites-enabled/default

# Copy your config
sudo cp deploy/nginx.conf /etc/nginx/sites-available/souled

# Create symbolic link
sudo ln -s /etc/nginx/sites-available/souled /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```

---

## Part 7: SSL Setup (Let's Encrypt)

### Option A: With Domain Name

```bash
# Edit SSL setup script
nano deploy/setup_ssl.sh

# Update DOMAIN and EMAIL
# Then run:
chmod +x deploy/setup_ssl.sh
./deploy/setup_ssl.sh
```

### Option B: Manual Setup

```bash
# Obtain certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Test auto-renewal
sudo certbot renew --dry-run
```

---

## Part 8: Configure Domain DNS (If Using Custom Domain)

### Update DNS Records

Add these records in your domain registrar:

| Type | Name | Value       | TTL |
| ---- | ---- | ----------- | --- |
| A    | @    | YOUR-EC2-IP | 300 |
| A    | www  | YOUR-EC2-IP | 300 |

Wait 5-30 minutes for DNS propagation.

---

## Part 9: Configure Stripe Webhooks

1. Go to [Stripe Dashboard](https://dashboard.stripe.com/webhooks)
2. Click "Add endpoint"
3. **Endpoint URL**: `https://your-domain.com/api/orders/webhook/`
4. **Events to send**:
   - `checkout.session.completed`
   - `payment_intent.succeeded`
5. Click "Add endpoint"
6. Copy **Signing secret** (starts with `whsec_`)
7. Update `.env` file:
   ```bash
   nano .env
   # Update STRIPE_WEBHOOK_SECRET
   sudo systemctl restart gunicorn
   ```

---

## Part 10: Update Frontend

Update your Vercel frontend environment variables:

1. Go to Vercel Dashboard → Your Project → Settings → Environment Variables
2. Update `VITE_API_URL`:
   ```
   https://your-domain.com/api
   ```
3. Redeploy frontend

---

## Maintenance & Monitoring

### View Logs

```bash
# Gunicorn logs
sudo journalctl -u gunicorn -f

# Nginx access logs
sudo tail -f /var/log/nginx/souled_access.log

# Nginx error logs
sudo tail -f /var/log/nginx/souled_error.log
```

### Deploy Updates

```bash
cd /home/ubuntu/souled-backend
chmod +x deploy/deploy.sh
./deploy/deploy.sh
```

### Restart Services

```bash
# Restart Gunicorn
sudo systemctl restart gunicorn

# Restart Nginx
sudo systemctl restart nginx

# Restart both
sudo systemctl restart gunicorn nginx
```

### Database Backup

```bash
# Backup from Supabase Dashboard
# Go to Database → Backups → Download

# Or use pg_dump
pg_dump "YOUR-SUPABASE-CONNECTION-STRING" > backup.sql
```

---

## Troubleshooting

### Issue: 502 Bad Gateway

**Solution**:

```bash
# Check Gunicorn status
sudo systemctl status gunicorn

# Check logs
sudo journalctl -u gunicorn -n 50

# Restart Gunicorn
sudo systemctl restart gunicorn
```

### Issue: Static Files Not Loading

**Solution**:

```bash
# Collect static files
source venv/bin/activate
python manage.py collectstatic --noinput

# Check permissions
sudo chown -R ubuntu:www-data staticfiles/
sudo chmod -R 755 staticfiles/

# Restart Nginx
sudo systemctl restart nginx
```

### Issue: Database Connection Error

**Solution**:

- Verify Supabase connection string in `.env`
- Check if Supabase project is active
- Test connection:
  ```bash
  psql "YOUR-SUPABASE-CONNECTION-STRING"
  ```

### Issue: CORS Errors

**Solution**:

```bash
# Update .env
nano .env

# Add your Vercel URL to CORS_ALLOWED_ORIGINS and CSRF_TRUSTED_ORIGINS
# Restart Gunicorn
sudo systemctl restart gunicorn
```

---

## Security Checklist

- ✅ DEBUG=False in production
- ✅ Strong SECRET_KEY generated
- ✅ HTTPS enabled with SSL certificate
- ✅ Secure cookies enabled
- ✅ Firewall configured (UFW)
- ✅ SSH key-based authentication
- ✅ Regular system updates
- ✅ Supabase connection over SSL
- ✅ Environment variables secured

---

## Cost Optimization

### Free Tier Limits

**AWS EC2**:

- 750 hours/month of t2.micro (1 instance running 24/7)
- Valid for first 12 months

**Supabase**:

- 500MB database storage
- 2GB bandwidth
- Unlimited API requests

### Monitor Usage

```bash
# Check disk usage
df -h

# Check memory usage
free -h

# Check running processes
htop
```

---

## Next Steps

1. ✅ Test all API endpoints
2. ✅ Test frontend integration
3. ✅ Test Stripe payments
4. ✅ Test Google OAuth
5. ✅ Set up monitoring (optional: CloudWatch, Sentry)
6. ✅ Configure automated backups
7. ✅ Set up CI/CD (optional: GitHub Actions)

---

## Support

- **Django Docs**: https://docs.djangoproject.com/
- **Nginx Docs**: https://nginx.org/en/docs/
- **Supabase Docs**: https://supabase.com/docs
- **Let's Encrypt**: https://letsencrypt.org/docs/

---

**Congratulations! Your Django backend is now live on AWS EC2! 🎉**
