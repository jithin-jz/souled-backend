<div align="center">

# 🛍️ Souled Store - Backend

### Modern E-Commerce API Engine built with Django REST Framework

[![Django](https://img.shields.io/badge/Django-5.2.8-092E20?style=for-the-badge&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/DRF-3.16.1-ff1709?style=for-the-badge&logo=django&logoColor=white)](https://www.django-rest-framework.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)

**A production-ready infrastructure** featuring JWT authentication, Stripe payment integration, and cloud-optimized media storage.


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

## 📸 App Screenshots

| Home | Products |
| :---: | :---: |
| ![Home](screenshots/home.png) | ![Products](screenshots/products.png) |

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

## ⚙️ Project Specifications

| 🛡️ Security Features | 🛠️ Technology Stack | 📝 Environment Variables |
| :--- | :--- | :--- |
| • **Rate Limiting**: `django-ratelimit` | • **Framework**: Django 5.2.8 | • `SECRET_KEY`: Django Key |
| • **Auth**: `SimpleJWT` + Cookies | • **API Layer**: DRF 3.16.1 | • `DATABASE_URL`: Postgres Link |
| • **Integrity**: `Django ORM` | • **Database**: PostgreSQL | • `CLOUDINARY_*`: Media API |
| • **Isolation**: `CORS Headers` | • **Auth**: SimpleJWT & Google | • `STRIPE_*`: Payment Keys |
| • **SQLi Protection**: Built-in ORM | • **Media**: Cloudinary | • `GOOGLE_CLIENT_ID`: OAuth |
| • **XSS Resistance**: HttpOnly Cookies | • **Payments**: Stripe Checkout | • `DEBUG`: Dev/Prod Mode |

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

## 📄 License

This project is licensed under the **MIT License**.

---

<div align="center">

<sub>Built with ❤️ by **JITHIN**</sub>

<br/>

[![GitHub stars](https://img.shields.io/github/stars/jithin-jz/souled-backend?style=social)](https://github.com/jithin-jz/souled-backend)
[![GitHub forks](https://img.shields.io/github/forks/jithin-jz/souled-backend?style=social)](https://github.com/jithin-jz/souled-backend/fork)

</div>