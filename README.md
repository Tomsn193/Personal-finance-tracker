# Finance Manager

A web-based personal finance management application built with Django. Track your income, expenses, set budgets, and visualize your financial data with ease.

## Features

✨ **Core Features:**
- 💰 Track income and expenses
- 📊 Visual dashboard with charts and statistics
- 🏷️ Customizable transaction categories
- 💳 Monthly budget management and tracking
- 📈 Financial reports and analytics
- 👤 User authentication and profiles
- 📱 Responsive design (mobile-friendly)

## Tech Stack

- **Backend:** Django 6.0.4
- **Database:** SQLite (Development) / PostgreSQL (Production)
- **Frontend:** Bootstrap 5, Chart.js
- **Authentication:** Django Built-in
- **Deployment:** Gunicorn, Whitenoise

## Installation

### Prerequisites
- Python 3.8+
- pip (Python package manager)
- Git

### Local Setup

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/finance-manager.git
cd finance-manager
```

2. **Create virtual environment**
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Create .env file** (for production settings)
```bash
# .env
SECRET_KEY=your-secret-key-here
DEBUG=False
DATABASE_URL=sqlite:///db.sqlite3
ALLOWED_HOSTS=localhost,127.0.0.1
```

5. **Run migrations**
```bash
python manage.py makemigrations
python manage.py migrate
```

6. **Create superuser** (admin account)
```bash
python manage.py createsuperuser
```

7. **Collect static files** (for production)
```bash
python manage.py collectstatic --noinput
```

8. **Run development server**
```bash
python manage.py runserver
```

Visit `http://localhost:8000` in your browser

## Usage

### Dashboard
The main dashboard displays:
- Current month's income and expenses summary
- Spending breakdown by category (pie chart)
- Budget status and progress
- Recent transactions

### Adding Transactions
1. Click "Add Transaction" button
2. Select transaction type (Income/Expense)
3. Enter amount and select category
4. Add optional description
5. Click "Save Transaction"

### Managing Budgets
1. Go to "Budgets" section
2. Click "Add Budget" to create monthly budget
3. Select category, set limit amount, choose month/year
4. Track spending against budget on dashboard

### Viewing Reports
1. Visit "Reports" section
2. Select month and year
3. View detailed breakdown:
   - Monthly income vs expenses
   - Spending by category
   - Net balance

### Managing Categories
1. Go to "Categories"
2. View all income and expense categories
3. Add custom categories
4. Delete unused categories

## Project Structure

```
finance-manager/
├── finance_project/          # Project settings
│   ├── settings.py          # Django configuration
│   ├── urls.py              # URL routing
│   └── wsgi.py              # WSGI application
├── transactions/             # Main app
│   ├── models.py            # Database models
│   ├── views.py             # View functions
│   ├── urls.py              # App URLs
│   ├── admin.py             # Admin configuration
│   └── migrations/          # Database migrations
├── templates/               # HTML templates
│   ├── base.html           # Base template
│   ├── login.html          # Login page
│   ├── register.html       # Registration page
│   ├── dashboard.html      # Dashboard
│   ├── transactions_list.html
│   ├── add_transaction.html
│   ├── edit_transaction.html
│   ├── categories.html
│   ├── budgets.html
│   ├── reports.html
│   └── settings.html
├── static/                  # Static files
│   ├── css/
│   │   ├── style.css       # Main stylesheet
│   │   └── auth.css        # Authentication pages
│   └── js/
│       └── main.js         # JavaScript functions
├── manage.py               # Django management script
├── requirements.txt        # Python dependencies
├── .gitignore             # Git ignore rules
├── README.md              # This file
└── db.sqlite3            # Development database
```

## Deployment

### Deploy to Heroku

1. **Install Heroku CLI**
```bash
# Download from https://devcenter.heroku.com/articles/heroku-cli
```

2. **Login to Heroku**
```bash
heroku login
```

3. **Create Heroku app**
```bash
heroku create your-app-name
```

4. **Add PostgreSQL addon**
```bash
heroku addons:create heroku-postgresql:hobby-dev
```

5. **Set environment variables**
```bash
heroku config:set SECRET_KEY='your-secret-key'
heroku config:set DEBUG=False
heroku config:set ALLOWED_HOSTS='your-app-name.herokuapp.com'
```

6. **Create Procfile**
```bash
# In project root, create file: Procfile
web: gunicorn finance_project.wsgi --log-file -
release: python manage.py migrate
```

7. **Push to Heroku**
```bash
git push heroku main
```

8. **Create superuser**
```bash
heroku run python manage.py createsuperuser
```

### Deploy to PythonAnywhere

1. Sign up at https://www.pythonanywhere.com/

2. Upload your code:
   - Via Git or ZIP upload
   
3. Create web app:
   - Choose Python version
   - Select Django web framework

4. Configure settings:
   - Set `DEBUG=False` in settings.py
   - Update `ALLOWED_HOSTS`
   - Set up static files path

5. Create database:
```bash
python manage.py migrate
python manage.py createsuperuser
```

6. Reload web app

### Deploy to Railway

1. Sign up at https://railway.app/

2. Create new project

3. Connect GitHub repository

4. Add PostgreSQL plugin

5. Set environment variables in Railway dashboard

6. Deploy automatically on push to main branch

## Database Models

### User Profile
- Extended user information
- Currency preference

### Category
- Name and type (income/expense)
- Custom colors for visualization
- User-specific

### Transaction
- Amount and type
- Category association
- Date and description
- Tags for organization
- Timestamps for audit trail

### Budget
- Monthly budget limits per category
- Automatic spending tracking
- Visual progress indicators

## API Endpoints (Future)

The app is designed to support REST API via Django REST Framework:

```
GET    /api/transactions/
POST   /api/transactions/
GET    /api/categories/
GET    /api/budgets/
GET    /api/reports/
```

## Security Features

- ✅ User authentication required for all pages
- ✅ CSRF protection on all forms
- ✅ SQL injection prevention via ORM
- ✅ Password hashing and validation
- ✅ Secure session management
- ✅ User data isolation per account

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'django'"
**Solution:** Activate virtual environment and install requirements
```bash
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Issue: "No such table: transactions_transaction"
**Solution:** Run migrations
```bash
python manage.py migrate
```

### Issue: Static files not loading in production
**Solution:** Collect static files
```bash
python manage.py collectstatic --noinput
```

### Issue: "DisallowedHost at /dashboard/"
**Solution:** Update ALLOWED_HOSTS in settings.py

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## Roadmap

- [ ] Recurring transaction automation
- [ ] Transaction import from CSV
- [ ] Bank API integration (Plaid)
- [ ] Mobile app (React Native)
- [ ] Export to PDF/Excel
- [ ] Savings goals tracking
- [ ] Investment portfolio tracking
- [ ] Multi-currency support
- [ ] Dark mode UI
- [ ] Advanced analytics

## License

This project is licensed under the MIT License - see LICENSE file for details.

## Support

For issues and questions:
1. Check existing issues on GitHub
2. Create a new issue with detailed description
3. Include steps to reproduce
4. Attach screenshots if applicable

## Changelog

### v1.0.0 (2026-04-19)
- Initial release
- Core finance tracking features
- Dashboard and reports
- Budget management
- User authentication

## Author

Your Name - [@yourtwitter](https://twitter.com/yourtwitter)

## Acknowledgments

- Django community
- Bootstrap for UI framework
- Chart.js for data visualization
- All contributors and supporters

---

Made with ❤️ by Your Name