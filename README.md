# Chapter 6: A Plot Twist - Bookstore Management System

A comprehensive Flask-based bookstore management system with automated setup, admin features, and order management capabilities.

## Quick Start for New Team Members

### Prerequisites
Make sure you have these installed:
- **Python 3.7+** - Download from [python.org](https://python.org)
- **Git** - Download from [git-scm.com](https://git-scm.com)
- **Visual Studio Code** (recommended) - Download from [code.visualstudio.com](https://code.visualstudio.com)

### Setup Instructions

1. **Clone the Repository**
   ```bash
   git clone https://github.com/samiikat90/Bookstore_Management_System.git
   cd Bookstore_Management_System
   ```

2. **Install Python Dependencies**
   ```bash
   pip install flask flask-sqlalchemy flask-login werkzeug
   ```

3. **Start the Application**
   ```bash
   # Option 1: Quick start (Windows)
   .\start.ps1
   
   # Option 2: Manual start (All platforms)
   python app/app.py
   ```

4. **Access the Bookstore**
   - Open your browser to: **http://127.0.0.1:5000**
   - **Use your assigned login credentials** (see table below)
   - Each team member has their own individual account

### Login Credentials
Each team member has their own admin account, all using the same password for convenience:

| Team Member | Username | Password | Email |
|-------------|----------|----------|-------|
| Samantha Franco | sfranco | admin123 | samiikat90@gmail.com |
| Becky Morris | bmorris | admin123 | mbrmorris@gmail.com |
| Felicia Brown | fbrown | admin123 | felicia.brown.711@gmail.com |
| Anthony Murphy | amurphy | admin123 | almurphy469@gmail.com |

**Additional System Accounts:**
| Username | Password | Email | Purpose |
|----------|----------|-------|---------|
| admin | admin123 | admin@plottwist.com | System Administrator |
| manager1 | admin123 | manager1@plottwist.com | Store Manager |
| supervisor | admin123 | supervisor@plottwist.com | Store Supervisor |

**Note**: After entering your username/password, you'll need to check your email for a 6-digit security code to complete login (Two-Factor Authentication).

## What's Included Out of the Box

The system comes pre-populated with sample data:
- **15 Popular Books** - Ready-to-manage inventory
- **Team Member Accounts** - Individual logins for each team member
- **15 Sample Orders** - Different statuses for testing
- **Complete Admin Dashboard** - Full functionality ready to use

## Key Features

### Admin Dashboard
- Real-time inventory and order tracking
- Interactive management interface
- User management capabilities

### Inventory Management
- Add, edit, and delete books
- CSV import/export functionality
- Stock tracking and management
- Professional book catalog with search

### Order Management
- View and process customer orders
- Update order statuses (Pending → Processing → Shipped → Completed)
- Bulk order operations
- Email notifications for status changes

### Security Features
- Two-Factor Authentication (2FA) via email
- Secure password hashing
- Session management
- Admin-only access controls

## Automated Scripts

### For Quick Operations:
```bash
# Start the application with database check
.\start.ps1

# Reset database with fresh sample data
.\reset_database.ps1

# Check current database status
python scripts/db_status.py

# View all user accounts
python scripts/check_users.py

# Reset passwords (if needed)
python scripts/reset_password.py
```

### For Development:
```bash
# Create fresh sample data
python scripts/setup_database.py

# Standardize all admin passwords
python scripts/standardize_passwords.py
```

## File Structure

```
Bookstore_Management_System/
├── app/
│   ├── app.py              # Main Flask application
│   └── templates/          # HTML templates
├── scripts/                # Automation scripts
│   ├── setup_database.py   # Create sample data
│   ├── db_status.py       # Check database
│   ├── reset_password.py   # Reset user passwords
│   └── standardize_passwords.py
├── instance/               # Database storage (auto-created)
├── uploads/                # CSV files
├── start.ps1              # Quick start script
├── reset_database.ps1     # Database reset script
├── QUICK_START.md         # Detailed setup guide
└── requirements.txt       # Python dependencies
```

## Troubleshooting

### Common Issues:

**"Python not found"**
- Install Python and ensure it's added to your system PATH

**"Permission denied" (Windows PowerShell)**
```powershell
# Run as Administrator:
Set-ExecutionPolicy RemoteSigned
```

**"Module not found" errors**
```bash
pip install flask flask-sqlalchemy flask-login werkzeug
```

**Can't access website**
- Make sure Flask is running (look for "Running on http://127.0.0.1:5000")
- Check the correct URL: http://127.0.0.1:5000

**Email/2FA issues**
- Check your email (including spam folder) for the 6-digit code
- Codes expire in 10 minutes - request a new one if needed

### Getting Help:
1. Check terminal output for error messages
2. Review `QUICK_START.md` for detailed instructions
3. Use `python scripts/db_status.py` to check system status
4. Contact team lead if issues persist

## Development Workflow

### Making Changes:
1. Edit files in VS Code
2. Test locally with `.\start.ps1`
3. Commit changes:
   ```bash
   git add .
   git commit -m "Describe your changes"
   git push origin main
   ```

### Reset to Clean State:
```bash
.\reset_database.ps1
```

## Team Notes

- **All passwords are standardized** to `admin123` for easy development access
- **Sample data regenerates** automatically when database is empty
- **Two-Factor Authentication** is required for all admin access
- **Email notifications** are configured and working for order updates
- **CSV import/export** supports large inventories with proper formatting

## Technologies Used

- **Backend**: Flask, SQLAlchemy, Flask-Login
- **Frontend**: Bootstrap 4, Font Awesome, jQuery
- **Database**: SQLite (development) with full schema
- **Security**: 2FA, password hashing, session management
- **Email**: Gmail SMTP for notifications and 2FA codes

---

## Quick Reference Commands

```bash
# Start application
.\start.ps1

# Reset everything
.\reset_database.ps1

# Check status
python scripts/db_status.py

# Access application
http://127.0.0.1:5000

# Login with your individual account
Username: [your assigned username] (sfranco, bmorris, fbrown, or amurphy)
Password: admin123
```

For detailed setup instructions, see `QUICK_START.md`.

---

**Repository**: https://github.com/samiikat90/Bookstore_Management_System  
**Last Updated**: October 30, 2025
