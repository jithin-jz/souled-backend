<div align="center">

# 🛍️ Souled Store - Backend

### Modern E-Commerce API Engine built with Django REST Framework

[![Django](https://img.shields.io/badge/Django-5.2.8-092E20?style=for-the-badge&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/DRF-3.16.1-ff1709?style=for-the-badge&logo=django&logoColor=white)](https://www.django-rest-framework.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)

**A production-ready infrastructure** featuring JWT authentication, Stripe payment integration, and cloud-optimized media storage.

[Features](#-key-capabilities) • [Quick Start](#-getting-started) • [Deployment](#-deployment-ready) • [Tech Stack](#-technology-stack)

</div>

---

## ✨ Key Capabilities

### 🔐 Security & Identity
- **Next-Gen Auth**: Secure JWT via HttpOnly cookies with automatic token refresh.
- **Social Integration**: Seamless Google OAuth integration for one-tap sign-in.
- **Robust Protection**: Built-in rate limiting (registration/login) and CSRF/CORS security.
- **Granular Control**: Staff-only permissions for product management and administrative tasks.

### 🛒 Commerce Core
- **Advanced Catalog**: Full CRUD capabilities with high-performance search and filtering.
- **Persistent Shopping**: Database-backed cart and wishlist that stays with the user across devices.
- **Order Lifecycle**: Comprehensive order management from creation to final status tracking.
- **Inventory Engine**: Real-time stock validation and automated inventory tracking.

### 💳 Payments & Media
- **Stripe Checkout**: Native integration for secure, hosted card global payments.
- **Flexible Options**: Support for both Cash on Delivery (COD) and Digital Payments.
- **Cloud Media**: Direct integration with Cloudinary for fast, optimized image delivery via CDN.

---

## 🚀 Getting Started

### Prerequisites
- **Python** 3.11+
- **PostgreSQL** 13+
- **Cloudinary** & **Stripe** accounts

### Setup Guide

1. **Environment Setup**
   ```bash
   git clone <your-repo-url>
   cd sBackend
   python -m venv .venv
   source .venv/bin/activate # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configuration**
   Create a `.env` file in the root directory:
   ```env
   SECRET_KEY=your_secret_key
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1
   DATABASE_URL=postgresql://user:password@localhost:5432/souled_db
   CLOUDINARY_URL=cloudinary://api_key:api_secret@cloud_name
   STRIPE_SECRET_KEY=sk_test_...
   GOOGLE_CLIENT_ID=your_id.apps.googleusercontent.com
   ```

3. **Initialize Database**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py import_products # Optional seeding
   ```

4. **Launch**
   ```bash
   python manage.py runserver
   ```
   > [!TIP]
   > The API will be accessible at `http://localhost:8000`.

---

## 🏗️ Project Architecture

```mermaid
graph TD
    A[Public API] --> B{Router}
    B --> C[Accounts]
    B --> D[Products]
    B --> E[Cart/Wishlist]
    B --> F[Orders]
    B --> G[Admin Panel]
    
    C --> H[(PostgreSQL)]
    D --> H
    E --> H
    F --> H
    
    F --> I[Stripe API]
    D --> J[Cloudinary CDN]
```

```text
sBackend/
├── accounts/      # Auth, JWT, Google OAuth
├── products/      # Catalog & Inventory
├── cart/          # Shopping Cart & Wishlist
├── orders/        # Payments & Processing
├── panel/         # Admin System
└── store/         # Core Settings
```

---

## 🛡️ Security Features

| Feature | Implementation | benefit |
| :--- | :--- | :--- |
| **Rate Limiting** | `django-ratelimit` | Brute-force protection |
| **Auth** | `SimpleJWT` + Cookies | XSS resistant sessions |
| **Integrity** | `Django ORM` | Prevention of SQL Injection |
| **Isolation** | `CORS Headers` | Controlled cross-origin access |

---

## 🚢 Deployment Ready

### Stack Recommendation
- **Runtime**: Python 3.11 on Ubuntu
- **Process Manager**: Gunicorn
- **Reverse Proxy**: NGINX with SSL
- **Database**: PostgreSQL (AWS RDS recommended)
- **Media**: Cloudinary (Automatic CDN)

> [!CAUTION]
> Always run `python manage.py check --deploy` before pushing to production to ensure all security settings are correctly configured.

---

## 🛠️ Technology Stack

| Component | Technology |
| :--- | :--- |
| **Backend Framework** | Django 5.2.8 |
| **API Layer** | Django REST Framework 3.16.1 |
| **Database** | PostgreSQL |
| **Authentication** | SimpleJWT & Google OAuth |
| **Media Storage** | Cloudinary |
| **Payment Gateway** | Stripe Checkout |

---

## 📝 Environment Variables

| Variable | Required | Description |
| :--- | :---: | :--- |
| `SECRET_KEY` | ✅ | Django cryptographic signing key |
| `DATABASE_URL` | ✅ | PostgreSQL connection string |
| `CLOUDINARY_*` | ✅ | Cloudinary API credentials |
| `STRIPE_*` | ✅ | Stripe secret and webhook keys |
| `GOOGLE_CLIENT_ID`| ✅ | Google OAuth credentials |
| `DEBUG` | ❌ | Set to `False` in production |

---

## 📄 License

This project is licensed under the **MIT License**.

---

<div align="center">

**Built with ❤️ by [JITHIN](https://github.com/jithin-jz)**

If you found this helpful, give it a ⭐!

</div>
