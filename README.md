# Chapter 6: A Plot Twist - Bookstore Management System

A comprehensive Flask-based bookstore management system with advanced features including two-factor authentication, payment validation, email notifications, comprehensive genre system, and customer data encryption.

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
   # Install all required packages from requirements.txt
   pip install -r requirements.txt
   
   # Or install individually if needed:
   pip install flask flask-sqlalchemy flask-login werkzeug cryptography blinker
   ```

3. **Start the Application**
   ```bash
   # Option 1: Automated setup with virtual environment (Recommended)
   .\run.ps1 -setup
   .\run.ps1
   
   # Option 2: Quick start (Windows)
   .\run.ps1
   
   # Option 3: Manual start (All platforms)
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

### Core E-commerce Platform
- **Complete Shopping Cart System** - Add, remove, update quantities with persistent storage
- **Guest Checkout** - Purchase without account creation, with email confirmations
- **Customer Registration & Login** - Full account management with order history
- **Advanced Product Catalog** - Professional book display with genre badges
- **Search & Filtering** - Find books by title, author, or genre

### Advanced Security Features
- **Two-Factor Authentication (2FA)** - Email-based security codes for all admin access
- **Customer Data Encryption** - Sensitive information encrypted at rest using Fernet
- **Secure Password Hashing** - Industry-standard password protection
- **Session Management** - Automatic timeout and browser-close detection
- **Admin Role Control** - Manager-level access controls

### Payment & Order Processing
- **Payment Validation System** - Luhn algorithm for credit cards, PayPal/bank validation
- **Multiple Payment Methods** - Credit card, PayPal, bank transfer support
- **Order Status Tracking** - Complete lifecycle from pending to delivered
- **Email Notifications** - Automated customer confirmations and admin alerts
- **Purchase History** - Detailed order tracking for customers

### Inventory Management
- **Complete CRUD Operations** - Add, edit, delete books with validation
- **CSV Import/Export** - Bulk inventory management with error handling
- **Genre Classification** - 20+ predefined genres with visual badges
- **Quantity Management** - Partial and full stock deletion with safety checks
- **Stock Tracking** - Real-time inventory updates

### Admin Dashboard
- **Real-time Analytics** - Order, inventory, and user management
- **Bulk Operations** - Mass order updates and inventory changes
- **User Management** - Create and manage admin accounts
- **Email System Integration** - SMTP configuration with Gmail
- **Data Export** - CSV exports for orders and purchases

### Professional UI/UX
- **Bootstrap 4 Framework** - Responsive, mobile-first design
- **Font Awesome Icons** - Professional iconography throughout
- **Genre Badges** - Visual categorization on all book displays
- **Status Indicators** - Color-coded order and inventory status
- **Loading States** - User feedback for all operations

## Automated Scripts

### For Quick Operations:
```bash
# Start with virtual environment (Recommended)
.\run.ps1 -setup    # First time setup
.\run.ps1           # Regular startup

# Legacy startup options
.\start.ps1         # Quick start without venv
python app/app.py   # Direct start

# Database management
.\reset_database.ps1    # Reset with fresh sample data
python scripts/db_status.py    # Check database status

# User management
python scripts/check_users.py    # View all accounts
python scripts/reset_password.py    # Reset passwords if needed
```

### For Development & Testing:
```bash
# Sample data creation
python scripts/setup_database.py    # Create fresh sample data
python scripts/standardize_passwords.py    # Standardize admin passwords

# Payment system testing
python test_payment_validation.py    # Test payment validation

# Database schema checks
python scripts/check_db_schema.py    # Verify database structure

# Encryption migration (if needed)
python migrate_encryption.py    # Migrate to encrypted customer data
```

## File Structure

```
Bookstore_Management_System/
├── app/
│   ├── app.py                    # Main Flask application
│   ├── payment_utils.py         # Payment validation (Luhn algorithm)
│   ├── payment_validator.py     # Payment method validation
│   └── templates/               # HTML templates
│       ├── index.html          # Homepage with genre badges
│       ├── cart.html           # Shopping cart interface
│       ├── payment.html        # Payment form with validation
│       ├── admin_dashboard.html # Admin control panel
│       ├── orders.html         # Order management
│       ├── purchases.html      # Purchase tracking
│       └── ...                 # Additional templates
├── scripts/                     # Automation scripts
│   ├── setup_database.py       # Create sample data
│   ├── check_db_schema.py      # Database structure validation
│   ├── db_status.py            # System status check
│   ├── reset_password.py       # Password reset utility
│   └── standardize_passwords.py
├── instance/                    # Database storage (auto-created)
│   └── uploads/                # File upload storage
├── uploads/                     # CSV files and exports
│   ├── BookListing.csv         # Sample inventory data
│   └── UpdatedBookListing.csv  # Updated inventory
├── tests/                       # Test files
│   └── test_payment_validation.py # Payment system tests
├── Documentation/               # Project documentation
│   ├── AGILE_DOCUMENTATION.md  # Sprint logs and retrospectives
│   ├── USER_STORIES.md         # Complete user story backlog
│   ├── PRODUCT_BACKLOG.md      # Feature prioritization
│   └── FINAL_FEATURE_SUMMARY.md # Feature completion summary
├── run.ps1                     # Automated setup with virtual environment
├── start.ps1                   # Quick start script
├── reset_database.ps1          # Database reset script
├── requirements.txt            # Python dependencies
├── migrate_encryption.py       # Customer data encryption migration
├── test_payment_validation.py  # Payment validation testing
└── README.md                   # This file
```

## Troubleshooting

### Common Issues:

**"Python not found"**
- Install Python and ensure it's added to your system PATH
- Try using `python3` instead of `python` on some systems

**"Permission denied" (Windows PowerShell)**
```powershell
# Run as Administrator:
Set-ExecutionPolicy RemoteSigned
```

**"Module not found" errors**
```bash
# Install all dependencies:
pip install -r requirements.txt

# Or install specific missing modules:
pip install flask flask-sqlalchemy flask-login werkzeug cryptography
```

**"Virtual environment issues"**
```bash
# Reset virtual environment:
rm -rf venv  # or Remove-Item venv -Recurse on Windows
.\run.ps1 -setup
```

**Can't access website**
- Make sure Flask is running (look for "Running on http://127.0.0.1:5000")
- Check the correct URL: http://127.0.0.1:5000
- Try a different port if 5000 is in use

**Email/2FA issues**
- Check your email (including spam folder) for the 6-digit code
- Codes expire in 10 minutes - request a new one if needed
- Ensure your email is correctly configured in your user account

**Payment validation errors**
- Use test credit card numbers for development (see payment_utils.py)
- Ensure payment form fields are properly filled
- Check browser console for JavaScript errors

**Database issues**
```bash
# Check database status:
python scripts/check_db_schema.py

# Reset database if corrupted:
.\reset_database.ps1

# Migrate encryption if needed:
python migrate_encryption.py
```

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
- **Payment validation** includes Luhn algorithm for credit cards
- **Customer data encryption** protects sensitive information at rest
- **Genre system** displays consistently across all templates
- **Guest checkout** supports customers without accounts
- **Comprehensive documentation** available in /Documentation folder

## Technologies Used

- **Backend**: Flask 3.1.2, SQLAlchemy 2.0.44, Flask-Login 0.6.3
- **Frontend**: Bootstrap 4, Font Awesome, jQuery
- **Database**: SQLite (development) with full schema and encryption
- **Security**: 2FA, password hashing, session management, data encryption
- **Email**: Gmail SMTP for notifications and 2FA codes
- **Payment**: Luhn algorithm validation, multiple payment methods
- **Development**: Virtual environment support, automated testing

---

## Quick Reference Commands

```bash
# Setup and start (Recommended for new setup)
.\run.ps1 -setup    # First time: creates venv and installs dependencies
.\run.ps1           # Start application with virtual environment

# Alternative startup methods
.\start.ps1         # Quick start without virtual environment
python app/app.py   # Direct start

# Database operations
.\reset_database.ps1           # Reset with fresh data
python scripts/check_db_schema.py    # Verify database structure
python migrate_encryption.py         # Migrate to encrypted data

# Testing and validation
python test_payment_validation.py    # Test payment system
python scripts/db_status.py         # Check system status

# Access application
http://127.0.0.1:5000

# Login with your individual account
Username: [your assigned username] (sfranco, bmorris, fbrown, or amurphy)
Password: admin123
# Then check email for 6-digit 2FA code
```

For detailed setup instructions, see the comprehensive documentation in the `/Documentation` folder.

---

**Repository**: https://github.com/samiikat90/Bookstore_Management_System  
**Last Updated**: November 5, 2025  
**Current Version**: 1.0 - Full E-commerce Platform with Advanced Features
