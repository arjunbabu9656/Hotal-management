# Hotel Food Management System

A production-ready Django application for hotel food ordering with three distinct role-based interfaces.

## 🚀 Features

- **Customer Interface**: Browse menu, add to cart, place orders, and track order status.
- **Staff Interface**: Kitchen dashboard for managing active orders and toggling menu availability.
- **Manager Interface**: Full dashboard with statistics, order management, menu CRUD, and reporting.

## 🛠 Tech Stack

- **Backend**: Python 3.x, Django 4.x
- **Frontend**: Bootstrap 5, Vanilla JS, Font Awesome 6
- **Database**: SQLite (Development)
- **Styling**: django-crispy-forms with Bootstrap 5

## 📦 Installation

1. Clone the repository and navigate to the project folder.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run migrations:
   ```bash
   python manage.py migrate
   ```
4. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```
5. Start the development server:
   ```bash
   python manage.py runserver
   ```

## 👥 User Roles

- **Customer**: Registered users who can place orders.
- **Staff**: Created by admin/manager to handle kitchen operations.
- **Manager**: Full access to all administrative features.

## 🔗 Key URLs

- Customer Menu: `/menu/`
- Staff Dashboard: `/staff/`
- Manager Dashboard: `/manager/`
- Admin Panel: `/admin/`
