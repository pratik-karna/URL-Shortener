# TrimLink - URL Shortener

A full-featured URL shortener web application built with Python and Django.

## Features

- **User Authentication** — Register, login, logout with session management
- **URL Shortening** — Base62 encoding algorithm for unique short code generation
- **URL Management** — View, edit, delete your short URLs from a dashboard
- **Click Analytics** — Track clicks with timestamps, IP address, and referrer
- **Custom Short Codes** — Set your own branded short URL code
- **Expiry Control** — Set links to expire after a specified number of hours
- **QR Code Generation** — Generate and download QR codes for any short URL
- **Responsive UI** — Clean, modern interface that works on all devices

## Tech Stack

- Python 3.10+
- Django 4.2
- SQLite (default, easily swappable to PostgreSQL)
- qrcode + Pillow (QR generation)
- Vanilla CSS (no framework dependencies)

## Setup & Installation

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/urlshortener.git
cd urlshortener
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run database migrations

```bash
python manage.py migrate
```

### 5. Create a superuser (optional, for admin panel)

```bash
python manage.py createsuperuser
```

### 6. Run the development server

```bash
python manage.py runserver
```

### 7. Open in browser

Visit: http://127.0.0.1:8000

Admin panel: http://127.0.0.1:8000/admin

## Project Structure

```
urlshortener/
├── manage.py
├── requirements.txt
├── README.md
├── db.sqlite3               # Created after first migration
├── urlshortener/            # Project config
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── shortener/               # Core URL shortener app
│   ├── models.py            # ShortURL + ClickAnalytics models
│   ├── views.py             # All views
│   ├── forms.py             # URL creation and edit forms
│   ├── urls.py
│   └── admin.py
├── accounts/                # Authentication app
│   ├── views.py
│   ├── forms.py
│   └── urls.py
├── templates/               # All HTML templates
│   ├── base.html
│   ├── shortener/
│   └── accounts/
└── static/
    └── css/style.css
```

## How the Short Code Algorithm Works

Short codes use **Base62 encoding**:
- Character set: `a-z`, `A-Z`, `0-9` (62 characters total)
- Random 6-character code generated per URL
- Collision checked against database before saving
- Custom codes validated for uniqueness and allowed characters

## Bonus Features Implemented

| Feature | Details |
|---|---|
| Custom Short Codes | Users can choose their own short code |
| Expiry Time | Set hours until a link expires |
| QR Code Generation | Downloadable PNG QR codes |
| Click Analytics | Per-click tracking with IP, referrer, timestamp |

## Deployment (Production)

For production deployment, update `settings.py`:
- Set `DEBUG = False`
- Set a strong `SECRET_KEY`
- Configure `ALLOWED_HOSTS`
- Switch to PostgreSQL database
- Serve static files via Nginx/WhiteNoise

Recommended free hosting: [Railway](https://railway.app) or [Render](https://render.com)
