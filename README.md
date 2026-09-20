# Wheelbase — Car Rental Management System

A full-stack car rental platform built with **Django** (backend + server-rendered
frontend) and **MongoDB** (via `mongoengine`) for persistent storage, with
custom session-based authentication.

## Tech stack

| Layer          | Technology                                             |
|----------------|---------------------------------------------------------|
| Backend        | Python 3.10+, Django 4.2                                |
| Database       | MongoDB (via `mongoengine` ODM)                          |
| Frontend       | Django templates, vanilla CSS + JS (no build step)       |
| Auth           | Custom session-based auth, PBKDF2 password hashing        |

> **Why is there also a `sessions_only.sqlite3` file?** Django's session
> framework needs a relational table to store session data. Every piece of
> *application* data (users, cars, bookings) lives in MongoDB — the sqlite
> file never stores anything but session keys.

## Project structure

```
car_rental_system/
├── manage.py
├── requirements.txt
├── .env.example
├── carrental/          # Django project settings, URLs, MongoDB connection
├── accounts/           # User model (MongoDB), register/login/logout, auth middleware
├── cars/               # Car model (MongoDB), home page, listing, detail, search/filter
├── bookings/           # Booking model (MongoDB), booking form, confirmation, cancellation
├── dashboard/           # User dashboard + "My Bookings"
├── adminpanel/          # Admin dashboard, manage cars/bookings/users
├── templates/           # Shared base template
└── static/              # CSS / JS
```

## 1. Prerequisites

- Python 3.10+
- MongoDB running locally (or an Atlas connection string)
  - macOS: `brew install mongodb-community && brew services start mongodb-community`
  - Ubuntu/Debian: `sudo apt install mongodb` (or use Docker, see below)
  - Docker: `docker run -d -p 27017:27017 --name wheelbase-mongo mongo:7`

## 2. Setup

```bash
cd car_rental_system

# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment config
cp .env.example .env
# Edit .env if your MongoDB isn't on localhost:27017,
# or paste a MONGO_URI if you're using MongoDB Atlas.

# Create Django's session table (sqlite — used only for sessions)
python manage.py migrate

# Seed sample cars + demo/admin accounts
python manage.py seed_data

# Run the development server
python manage.py runserver
```

Visit **http://127.0.0.1:8000/**.

## 3. Demo accounts (created by `seed_data`)

| Role  | Username | Password       |
|-------|----------|----------------|
| Admin | `admin`  | `Admin@12345`  |
| User  | `demo`   | `Demo@12345`   |

Log in as `admin` and visit **/manage/** for the admin dashboard, or log in
as `demo` (or register your own account) to browse and book cars.

## 4. Pages

| Page                | URL                              |
|---------------------|-----------------------------------|
| Home                | `/`                               |
| Cars (list/filter)  | `/cars/`                          |
| Car details         | `/cars/<car_id>/`                 |
| Register            | `/accounts/register/`             |
| Login               | `/accounts/login/`                |
| Booking form        | `/bookings/new/<car_id>/`         |
| Booking confirmation| `/bookings/confirmation/<id>/`    |
| User dashboard      | `/dashboard/`                     |
| My Bookings         | `/dashboard/my-bookings/`         |
| Admin dashboard     | `/manage/`                        |
| Manage cars         | `/manage/cars/`                   |
| Manage bookings     | `/manage/bookings/`               |
| Manage users        | `/manage/users/`                  |

## 5. How key requirements are implemented

- **Authentication**: `accounts.models.User` is a MongoDB document. Passwords
  are hashed with Django's own PBKDF2 hasher (`django.contrib.auth.hashers`),
  never stored in plain text. Login stores a `user_id` in the Django session;
  `accounts.middleware.MongoUserMiddleware` attaches the current user to every
  request as `request.mongo_user`. `accounts.decorators.login_required_mongo`
  and `admin_required` protect views.
- **Booking overlap prevention**: `bookings.utils.has_overlapping_booking`
  compares the requested pickup/drop-off window against every active
  (Pending/Confirmed) booking for that car and rejects the request if the
  ranges intersect.
- **Automatic price calculation**: `bookings.utils.calculate_total_price`
  bills at the daily rate (rounded up to whole days) for rentals ≥ 24 hours,
  and at the hourly rate (rounded up to whole hours) for shorter rentals.
  The client-side JS in `static/js/main.js` shows a live *estimate* only —
  the authoritative number is always (re)computed server-side on submit.
- **Validation**: Django forms validate all booking and car-management
  input (required fields, date/time ordering, no past pickup times, unique
  username/email, password strength via Django's validators, etc.).
- **Admin dashboard statistics**: total cars/available cars, total users,
  total bookings, revenue from confirmed+completed bookings, and a breakdown
  of bookings by status.

## 6. Notes on running this outside a live-tested environment

This project was written to be complete and internally consistent, but it
was **not executed end-to-end** in the environment that generated it (no
network access to install packages or run a MongoDB server there). Please
run it locally following the steps above. If you hit an import or dependency
version issue, check `requirements.txt` — pinned versions are known to work
together, but newer/older combinations of Django + mongoengine can have
compatibility quirks.
