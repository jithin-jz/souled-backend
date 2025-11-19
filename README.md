# Store Backend (Django REST API)

Modern e-commerce backend built with Django REST Framework. It provides JWT-authenticated user flows, catalog management, persistent carts and wishlists, order management, and Stripe-powered payments. Assets are stored on Cloudinary and the API is designed to be consumed by a SPA (default CORS origin is `http://localhost:5173`).

---

## Features
- Custom email-based user model with cookie-stored JWT sessions (access + refresh) and Google One-Tap login.
- Product catalog with search, category filter, price range filter, and slug generation plus a bulk import command that uploads product imagery to Cloudinary.
- Authenticated cart & wishlist APIs with quantity controls and duplicate prevention.
- Order pipeline supporting COD and Stripe Checkout, including webhook + fallback verification to keep order status in sync.
- Configurable CORS, CSRF, Cloudinary storage, and Stripe credentials via `.env`.

---

## Tech Stack
- Python 3.11+, Django 5, Django REST Framework
- SimpleJWT (cookie-based), django-cors-headers
- Cloudinary & django-cloudinary-storage for media
- Stripe Checkout API
- PostgreSQL (configured via `DATABASE_URL`) – swapable with any Django-supported DB

---

## Project Layout
```
store/           Django project (settings, urls, wsgi/asgi)
accounts/        Custom user model + auth endpoints
products/        Product catalog, serializers, import command
cart/            Cart & wishlist models/APIs
orders/          Orders, addresses, Stripe integration
products.json    Seed data used by import_products command
```

---

## Getting Started

### 1. Prerequisites
- Python 3.11+
- PostgreSQL (or adjust `DATABASE_URL` to SQLite for local experiments)
- Cloudinary account & API keys
- Stripe account + test keys

### 2. Setup
```bash
git clone <repo-url>
cd sBackend
python -m venv .venv
source .venv/Scripts/activate        # PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 3. Environment Variables
Create `.env` in the project root:
```
SECRET_KEY=django-secret
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
DATABASE_URL=postgres://user:pass@localhost:5432/store

CLOUDINARY_CLOUD_NAME=xxx
CLOUDINARY_API_KEY=xxx
CLOUDINARY_API_SECRET=xxx

STRIPE_SECRET_KEY=sk_test_xxx
STRIPE_PUBLISHABLE_KEY=pk_test_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx

GOOGLE_CLIENT_ID=<oauth-client-id>.apps.googleusercontent.com
FRONTEND_URL=http://localhost:5173
```

### 4. Database & Superuser
```bash
python manage.py migrate
python manage.py createsuperuser
```

### 5. Seed Product Catalog (optional)
`products/management/commands/import_products.py` pulls images, uploads to Cloudinary, and creates `Product` rows based on `products.json`.
```bash
python manage.py import_products
```

### 6. Run the API
```bash
python manage.py runserver
```

---

## API Overview

### Auth (`/api/auth/`)
- `POST register/` – create user and issue JWT cookies.
- `POST login/` – email/password login.
- `POST google/` – Google ID token login.
- `POST logout/` – clears access/refresh cookies.
- `GET me/` – current user profile (requires auth).

### Products (`/api/products/`)
- `GET /` – list products with `search`, `category`, `min_price`, `max_price` query params.
- `POST create/` – add product (admin/staff checks should be added in production).
- `GET|PUT|PATCH|DELETE <pk>/` – retrieve or mutate a product.

### Cart (`/api/cart/`)
- `GET /` – fetch authenticated user cart with expanded product data.
- `POST add/` – body `{product_id, quantity}`.
- `PATCH update/<item_id>/` – update quantity.
- `DELETE remove/<item_id>/` – remove item.

### Wishlist (`/api/cart/wishlist/`)
- `GET /` – fetch wishlist.
- `POST add/` – body `{product_id}`; duplicates return a friendly message.
- `DELETE remove/<item_id>/`

### Orders (`/api/orders/`)
- `POST create/` – payload includes `cart` (array of `{id,name,price,quantity}`), `address`, and `payment_method` (`cod` or `stripe`). Creates `Order`, `OrderItem`s, and either sets status to `processing` or returns a Stripe Checkout URL.
- `GET verify-payment/?session_id=...` – fallback polling to confirm Stripe sessions.
- `POST webhook/` – Stripe webhook endpoint; configure the CLI/dashboard to point to `/api/orders/webhook/`.
- `GET my/` – list authenticated user orders with nested items and formatted timestamps.

Authentication is enforced via `accounts.authentication.CookieJWTAuthentication`, which reads the `access` cookie SimpleJWT issues at login/registration. Ensure your frontend sends `credentials: 'include'` on fetch requests.

---

## Stripe & Webhooks
1. Start a local tunnel (e.g., `stripe listen --forward-to localhost:8000/api/orders/webhook/`).
2. Copy the signing secret into `STRIPE_WEBHOOK_SECRET`.
3. Use the Checkout session URL returned by `order/create/` to complete test payments (default currency INR).
4. Payment confirmation automatically updates order status via webhook; `verify-payment/` provides a manual fallback.

---

## Testing
Run Django tests (each app ships with `tests.py` placeholders ready for expansion):
```bash
python manage.py test
```

---

## Deployment Notes
- Set `DEBUG=False`, `CLOUDINARY_*`, Stripe keys, and `ALLOWED_HOSTS` correctly.
- Use HTTPS so cookies can be `Secure` and `SameSite=None` if your frontend is on a different origin.
- Production should switch `conn_max_age`/`ssl_require` for the target database and tighten CORS lists.

---

## Next Steps
- Enforce staff-only access to product mutation endpoints.
- Add rate limiting and email verification for new accounts.
- Flesh out automated tests for cart, order, and webhook flows.

