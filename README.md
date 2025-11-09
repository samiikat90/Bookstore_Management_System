# Chapter 6: A Plot Twist - Bookstore Management System

A comprehensive Flask-based bookstore management system with advanced features including two-factor authentication, payment validation, email notifications, comprehensive genre system, and customer data encryption.

## IMPORTANT: Setup Instructions for Team Members

### If you received the repository URL or ZIP file, follow these EXACT steps to avoid CSRF and other issues:

### Prerequisites
Make sure you have these installed BEFORE starting:
- **Python 3.7+** - Download from [python.org](https://python.org)
- **Git** - Download from [git-scm.com](https://git-scm.com) (if cloning from GitHub)
- **Visual Studio Code** (recommended) - Download from [code.visualstudio.com](https://code.visualstudio.com)

### STEP-BY-STEP SETUP PROCESS

#### Method 1: From GitHub URL (Recommended)

1. **Clone the Repository**
   ```bash
   git clone https://github.com/samiikat90/Bookstore_Management_System.git
   cd Bookstore_Management_System
   ```

2. **Set Up Python Virtual Environment (CRITICAL)**
   ```powershell
   # Windows PowerShell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   
   # If you get execution policy error, run this first:
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```
   
   ```bash
   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies (EXACT VERSIONS REQUIRED)**
   ```bash
   # Install all required packages with exact versions
   pip install -r requirements.txt
   
   # Verify installation
   pip list
   ```

4. **Create Environment Configuration**
   ```bash
   # Copy the example environment file
   copy .env.example .env    # Windows
   # OR
   cp .env.example .env      # macOS/Linux
   ```

5. **Initialize Database (REQUIRED)**
   ```bash
   # Create the database and populate with sample data
   python scripts/setup_database.py
   ```

6. **Start the Application**
   ```bash
   python app/app.py
   ```

#### Method 2: From ZIP File

1. **Extract the ZIP file** to your desired location

2. **Open Terminal/PowerShell** in the extracted folder

3. **Follow steps 2-6 from Method 1** exactly as written

### CSRF TOKEN ISSUE - SOLUTION

If you encounter "CSRF token missing" errors, this means the application setup wasn't completed properly. Here's the fix:

#### Quick Fix for CSRF Issues:
1. **Stop the application** (Ctrl+C in terminal)
2. **Delete the instance folder** if it exists:
   ```bash
   rmdir /s instance    # Windows
   rm -rf instance      # macOS/Linux
   ```
3. **Restart the setup process**:
   ```bash
   python scripts/setup_database.py
   python app/app.py
   ```

#### Why CSRF Errors Happen:
- Database not properly initialized
- Missing environment configuration
- Running without virtual environment
- Old/cached database files

### VERIFICATION STEPS

After setup, verify everything works:

1. **Check Database Status**:
   ```bash
   python scripts/check_db.py
   ```

2. **Test Login Process**:
   - Go to http://127.0.0.1:5000
   - Click "Admin Login" 
   - Use credentials: username: `admin`, password: `admin123`
   - Check email for 2FA code

3. **Verify CSRF Protection**:
   - Try adding a book to cart
   - Try accessing admin dashboard
   - No CSRF errors should appear

### LOGIN CREDENTIALS

Each team member has their own admin account:

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

**IMPORTANT**: After entering username/password, check your email for a 6-digit security code (Two-Factor Authentication).

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
.\run.ps1 -setup # First time setup
.\run.ps1 # Regular startup

# Legacy startup options
.\start.ps1 # Quick start without venv
python app/app.py # Direct start

# Database management
.\reset_database.ps1 # Reset with fresh sample data
python scripts/db_status.py # Check database status

# User management
python scripts/check_users.py # View all accounts
python scripts/reset_password.py # Reset passwords if needed
```

### For Development & Testing:
```bash
# Sample data creation
python scripts/setup_database.py # Create fresh sample data
python scripts/standardize_passwords.py # Standardize admin passwords

# Payment system testing
python test_payment_validation.py # Test payment validation

# Database schema checks
python scripts/check_db_schema.py # Verify database structure

# Encryption migration (if needed)
python migrate_encryption.py # Migrate to encrypted customer data
```

## File Structure

```
Bookstore_Management_System/
 app/
 app.py # Main Flask application
 payment_utils.py # Payment validation (Luhn algorithm)
 payment_validator.py # Payment method validation
 templates/ # HTML templates
 index.html # Homepage with genre badges
 cart.html # Shopping cart interface
 payment.html # Payment form with validation
 admin_dashboard.html # Admin control panel
 orders.html # Order management
 purchases.html # Purchase tracking
 ... # Additional templates
 scripts/ # Automation scripts
 setup_database.py # Create sample data
 check_db_schema.py # Database structure validation
 db_status.py # System status check
 reset_password.py # Password reset utility
 standardize_passwords.py
 instance/ # Database storage (auto-created)
 uploads/ # File upload storage
 uploads/ # CSV files and exports
 BookListing.csv # Sample inventory data
 UpdatedBookListing.csv # Updated inventory
 tests/ # Test files
 test_payment_validation.py # Payment system tests
 Documentation/ # Project documentation
 AGILE_DOCUMENTATION.md # Sprint logs and retrospectives
 USER_STORIES.md # Complete user story backlog
 PRODUCT_BACKLOG.md # Feature prioritization
 FINAL_FEATURE_SUMMARY.md # Feature completion summary
 run.ps1 # Automated setup with virtual environment
 start.ps1 # Quick start script
 reset_database.ps1 # Database reset script
 requirements.txt # Python dependencies
 migrate_encryption.py # Customer data encryption migration
 test_payment_validation.py # Payment validation testing
 README.md # This file
```

## Troubleshooting Common Issues

### CSRF Token Issues (Most Common)

**Error Message**: "CSRF token missing" or "The CSRF token is missing"

**Root Cause**: Database not properly initialized or application running without proper setup

**COMPLETE SOLUTION**:
1. **Stop the application** (Ctrl+C in terminal)
2. **Ensure virtual environment is active**:
   ```bash
   # Windows
   .\venv\Scripts\Activate.ps1
   
   # macOS/Linux  
   source venv/bin/activate
   ```
3. **Delete and recreate database**:
   ```bash
   # Remove corrupted database
   rmdir /s instance    # Windows
   rm -rf instance      # macOS/Linux
   
   # Recreate database with proper structure
   python scripts/setup_database.py
   ```
4. **Restart application**:
   ```bash
   python app/app.py
   ```
5. **Test immediately**: Go to http://127.0.0.1:5000 and try admin login

### Python Installation Issues

**"Python not found" or "python: command not found"**

**Solution**:
1. Download Python from [python.org](https://python.org) 
2. During installation, CHECK "Add Python to PATH"
3. Restart terminal/command prompt
4. Test with: `python --version`
5. If still not working, try `python3` instead of `python`

### Permission Issues (Windows PowerShell)

**Error**: "execution of scripts is disabled on this system"

**Solution**:
```powershell
# Run PowerShell as Administrator, then:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then restart normal PowerShell and try again
```

### Virtual Environment Issues

**"venv not working" or "module not found" errors**

**Complete Reset Solution**:
```bash
# Remove broken virtual environment
rmdir /s venv           # Windows
rm -rf venv            # macOS/Linux

# Create fresh virtual environment  
python -m venv venv

# Activate it
.\venv\Scripts\Activate.ps1    # Windows
source venv/bin/activate       # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Setup database
python scripts/setup_database.py

# Start application
python app/app.py
```

### Database Connection Issues

**"No such table" or "database locked" errors**

**Solution**:
```bash
# Check database status
python scripts/check_db.py

# If database is corrupted, reset it:
python scripts/setup_database.py

# If issues persist, delete everything and recreate:
rmdir /s instance
python scripts/setup_database.py
```

### Email/2FA Not Working

**"Didn't receive 2FA code" or "email not sending"**

**Troubleshooting Steps**:
1. **Check spam/junk folder** - codes often go there
2. **Wait 2-3 minutes** - email delivery can be slow
3. **Verify email address** in your user account settings
4. **Try different email** if persistent issues
5. **Check terminal output** for email errors

**Alternative**: Use the admin account (`admin`/`admin123`) with email: admin@plottwist.com

### Port Already in Use

**"Port 5000 is already in use"**

**Solution**:
```bash
# Find what's using port 5000:
netstat -ano | findstr :5000    # Windows
lsof -i :5000                   # macOS/Linux

# Kill the process using the port, then restart app
```

### Application Won't Start

**"ModuleNotFoundError" or import errors**

**Complete Fix**:
```bash
# 1. Verify virtual environment
.\venv\Scripts\Activate.ps1    # Windows
source venv/bin/activate       # macOS/Linux

# 2. Upgrade pip
python -m pip install --upgrade pip

# 3. Install dependencies fresh
pip uninstall -r requirements.txt -y
pip install -r requirements.txt

# 4. Setup database
python scripts/setup_database.py

# 5. Start application
python app/app.py
```

### Browser Issues

**"Can't access http://127.0.0.1:5000"**

**Solutions**:
1. **Verify Flask is running** - look for "Running on http://127.0.0.1:5000" in terminal
2. **Check URL spelling** - must be exactly `http://127.0.0.1:5000`
3. **Try different browser** - Chrome, Firefox, Edge
4. **Disable browser extensions** - they can interfere with local development
5. **Clear browser cache** - Ctrl+F5 or Cmd+Shift+R

### Payment System Issues

**Payment validation errors or "Invalid payment method"**

**For Testing Use These**:
```
Valid Test Credit Card: 4532015112830366
Valid PayPal Email: test@example.com
Valid Bank Account: 123456789 (routing: 021000021)
```

### If All Else Fails - Nuclear Reset

**Complete Fresh Start**:
```bash
# 1. Delete everything except source code
rmdir /s venv instance __pycache__    # Windows
rm -rf venv instance __pycache__      # macOS/Linux

# 2. Fresh virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1    # Windows
source venv/bin/activate       # macOS/Linux

# 3. Fresh dependencies
pip install -r requirements.txt

# 4. Fresh database
python scripts/setup_database.py

# 5. Test immediately
python app/app.py
# Go to http://127.0.0.1:5000
```

### Getting Additional Help

**If issues persist**:
1. **Check terminal output** for specific error messages
2. **Copy exact error text** when asking for help
3. **Include your operating system** (Windows 10/11, macOS, Linux)
4. **Try the "Nuclear Reset" above** before asking for help

**Contact Information**:
- Repository: https://github.com/samiikat90/Bookstore_Management_System
- Issues: Create an issue on GitHub with error details

### Quick Verification Checklist

After setup, verify these work:
- [ ] http://127.0.0.1:5000 loads the homepage
- [ ] Admin login works with `admin`/`admin123`
- [ ] 2FA email arrives (check spam folder)  
- [ ] Can access admin dashboard after 2FA
- [ ] Can add books to cart without CSRF errors
- [ ] Database has sample books and orders

If any of these fail, repeat the setup process from the beginning.

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
.\run.ps1 -setup # First time: creates venv and installs dependencies
.\run.ps1 # Start application with virtual environment

# Alternative startup methods
.\start.ps1 # Quick start without virtual environment
python app/app.py # Direct start

# Database operations
.\reset_database.ps1 # Reset with fresh data
python scripts/check_db_schema.py # Verify database structure
python migrate_encryption.py # Migrate to encrypted data

# Testing and validation
python test_payment_validation.py # Test payment system
python scripts/db_status.py # Check system status

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
**Last Updated**: November 9, 2025 
**Current Version**: 2.0 - Production Ready with Comprehensive Documentation
