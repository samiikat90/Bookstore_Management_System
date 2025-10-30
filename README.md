# Chapter-6-A-Plot-Twist — repository layout

This repo was reorganized to a conventional Flask layout.

Top-level structure
  - app.py — Flask app entrypoint (was Sprint1.py)
  - templates/ — HTML templates moved from `book_inventory/templates`
  - static/ — CSS/JS/assets

Run (using the project's virtualenv):
Windows PowerShell
```powershell
.\venv\Scripts\Activate.ps1
python -m app.app
```

Or using flask CLI from project root:
```powershell
$env:FLASK_APP='app.app'
flask run
```

# Chapter 6: A Plot Twist — Bookstore Management System

A comprehensive Flask-based bookstore management system with advanced security features and admin capabilities.

## Features

- **Two-Factor Authentication (2FA)** — Email-based security codes for admin login
- **Admin Dashboard** — Interactive cards for inventory, orders, and user management
- **Inventory Management** — Add, edit, delete books with CSV import/export
- **Order Management** — View, track, and update order statuses with email notifications
- **User Management** — Create and manage admin users with notification preferences
- **Email Notifications** — Automated alerts for new orders and status changes
- **Professional UI** — Bootstrap 4.5.2 with Font Awesome icons and responsive design

## Quick Start

1. **Clone and Set Up Environment**
   ```powershell
   git clone https://github.com/samiikat90/Chapter-6-A-Plot-Twist.git
   cd Chapter-6-A-Plot-Twist
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

2. **Configure Environment Variables**
   ```powershell
   copy .env.example .env
   notepad .env
   ```

3. **Run the Application**
   ```powershell
   .\run.ps1
   ```
   Or manually:
   ```powershell
   .\venv\Scripts\python.exe .\app\app.py
   ```

4. **Access the Application**
   - Visit: [http://127.0.0.1:5000](http://127.0.0.1:5000)
   - Login with existing admin accounts (2FA required)

## Admin Accounts (Pre-configured)

The system includes 5 admin users with 2FA enabled:
- **samiikat**: Email `samiikat90@gmail.com`
- **katrina**: Email `katrinastrain@gmail.com`
- **mike**: Email `mikezander@gmail.com`
- **sarah**: Email `sarah@gmail.com`
- **john**: Email `john@gmail.com`

Password: `admin123` for all accounts

## Project Structure

```
Chapter-6-A-Plot-Twist/
├── app/                    # Main Flask application
│   ├── app.py             # Flask app with all routes and models
│   └── templates/         # HTML templates
├── scripts/               # Utility scripts
│   ├── create_admin_users.py  # Create new admin users
│   ├── create_sample_*.py     # Generate sample data
│   └── check_db.py           # Database inspection
├── tests/                 # Test files
├── instance/              # Database and uploads (auto-created)
├── uploads/               # CSV files for import/export
├── .env                   # Environment configuration
└── requirements.txt       # Python dependencies
```

## Security Features

- **Two-Factor Authentication**: Email-based security codes with 10-minute expiration
- **Session Management**: Secure login sessions with Flask-Login
- **Password Hashing**: Werkzeug security for password protection
- **Email Verification**: Required 2FA verification for admin access

## Admin Features

### Dashboard
- Interactive navigation cards
- Auto-refresh every 60 seconds
- Real-time order and inventory counts

### Inventory Management
- Add new books individually
- Edit existing book details
- CSV import with scientific notation support
- CSV export with timestamps
- Stock tracking and management

### Order Management
- View all orders with filtering
- Update order statuses with bulk operations
- Email notifications to admin team
- Order tracking and history

### User Management
- Create new admin users
- Configure email notification preferences
- Manage user permissions

## Email Configuration

The system uses Gmail SMTP for notifications:
```
GMAIL_EMAIL=chapter6aplottwist@gmail.com
GMAIL_APP_PASSWORD=giuw lmir sdmo fgej
```

## Development

### Adding New Admin Users
```powershell
.\venv\Scripts\python.exe scripts\create_admin_users.py
```

### Database Management
```powershell
.\venv\Scripts\python.exe scripts\check_db.py
```

### Sample Data Generation
```powershell
.\venv\Scripts\python.exe scripts\create_sample_orders.py
.\venv\Scripts\python.exe scripts\create_sample_purchases.py
```

## Technologies Used

- **Backend**: Flask 3.1.2, SQLAlchemy 2.0.44, Flask-Login
- **Frontend**: Bootstrap 4.5.2, Font Awesome, jQuery
- **Database**: SQLite with comprehensive models
- **Email**: Gmail SMTP with MIMEText/MIMEMultipart
- **Security**: Two-factor authentication, password hashing

## License

This project is part of a workshop demonstration for bookstore management systems.

---

For support or questions, check the admin dashboard or contact system administrators.

---

Quick start (Windows PowerShell)
1. Create a virtualenv and install dependencies:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

2. Copy `.env.example` to `.env` and edit values (SECRET_KEY, Gmail creds if used):

### Order Confirmation Email Setup

Order confirmation emails are sent using Gmail SMTP. The app is now configured to use:

- Gmail: `chapter6aplottwist@gmail.com`
- App Password: `giuw lmir sdmo fgej`

These credentials are set in `.env` and `.env.example` as:

```
GMAIL_EMAIL=chapter6aplottwist@gmail.com
GMAIL_APP_PASSWORD=giuw lmir sdmo fgej
```

If you change the email or password, update both `.env` and `.env.example`.

```powershell
copy .env.example .env
notepad .env
```

3. Initialize the database and create a manager account:

```powershell
.\venv\Scripts\python.exe scripts\create_db.py
.\venv\Scripts\python.exe scripts\create_manager.py admin admin123
```

4. (Optional) Add sample data:

```powershell
.\venv\Scripts\python.exe scripts\create_sample_purchases.py
```

5. Run the app:

```powershell
.\venv\Scripts\python.exe app\app.py
```

Open http://127.0.0.1:5000 and login with the manager account to use the admin dashboard.

Helper scripts
- `run.ps1` — simple helper to set up venv and run the app on Windows.
- `.env.example` — example environment variables. Do not commit `.env` with real credentials.

Sharing
- Push to GitHub and tell peers to clone and follow these steps.
- Optionally create a ZIP of the repo (exclude `venv` and `instance`).
