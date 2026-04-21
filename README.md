# Finance Manager - Personal Finance Management Application

A powerful, modern Django-based personal finance management application with a beautiful web interface and REST API.

**[Live Demo on Render](https://www.google.com/search?q=https://your-app-name.onrender.com)** *(Replace with your actual link)*

-----

## Features

### Transaction Management

* **Full CRUD:** Create, read, update, and delete transactions.
* **Categorization:** Organize by Income/Expense with optional descriptions.
* **Smart Filtering:** Filter by category, type, and date with full input validation.

### Dashboard & Analytics

* **Real-time Summaries:** Instant view of income vs. expenses.
* **Visual Data:** Spending breakdown by category using **Chart.js**.
* **Flexible Periods:** Toggle between *This Month*, *This Year*, or *All Time*.

### Budget Management

* **Category Limits:** Create monthly budgets per category.
* **Progress Tracking:** Visual indicators to track spending vs. limits.

### User Management & Security

* **Data Isolation:** Users only see their own financial data.
* **Security First:** Features password hashing, CSRF protection, and SQL injection prevention.
* **Multi-Currency:** Support for 13+ currencies (USD, EUR, GBP, NGN, etc.).

### REST API

* **30+ Endpoints:** Fully documented API for mobile or third-party integration.
* **Token Auth:** Secure access via REST Framework tokens.

-----

## Project Structure

```text
finance_project/
├── finance_project/          # Main settings (settings.py, urls.py)
├── transactions/             # Main app (models, views, serializers)
├── templates/                # HTML templates (Bootstrap 5)
├── static/                   # CSS, JS, images
├── manage.py
└── requirements.txt
```

-----

## Tech Stack

* **Backend:** Django 6.0, Django REST Framework
* **Database:** PostgreSQL (Production), SQLite (Development)
* **Frontend:** Bootstrap 5, Chart.js
* **Deployment:** Render

-----

## Quick Start

### Prerequisites

* Python 3.9+
* pip & Virtual environment

### Local Installation

1. **Clone & Navigate**
   ```bash
   git clone https://github.com/yourusername/finance-manager.git
   cd finance-manager
   ```

2. **Setup Environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Database Setup**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py runserver
   ```

Visit: `http://localhost:8000/`

-----

## 🌐 Deployment (Render)

This project is configured for deployment on **Render** via `gunicorn`.

### Steps to Deploy your own:

1. **Create a Blueprint or Web Service:** Connect your GitHub repository to Render.

2. **Build Command:**
   ```bash
   pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
   ```

3. **Start Command:**
   ```bash
   gunicorn finance_project.wsgi:application
   ```

4. **Environment Variables:**
   * `DEBUG`: `False`
   * `SECRET_KEY`: Your secret key
   * `DATABASE_URL`: Your PostgreSQL connection string
   * `ALLOWED_HOSTS`: `your-app.onrender.com`

-----

## API Endpoints (Brief)

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/auth/token/` | Obtain Auth Token |
| `GET` | `/api/transactions/` | List all transactions |
| `GET` | `/api/dashboard/summary/` | Get financial stats |
| `POST` | `/api/budgets/` | Set a new budget |

-----

## License

MIT License - Free to use and modify.

-----

**Developed by [Your Name/Oduone]** | Version 1.0.0 | 🎉
