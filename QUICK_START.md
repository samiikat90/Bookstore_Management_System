# Quick Setup Guide

## Getting Started

### Option 1: Quick Start (Recommended)
```powershell
.\start.ps1
```
This will check your database and start the application.

### Option 2: Reset Everything
```powershell
.\reset_database.ps1
```
This will completely reset the database and add fresh sample data.

## Available Scripts

### PowerShell Scripts
- `start.ps1` - Quick start with database status check
- `reset_database.ps1` - Complete database reset with sample data

### Python Scripts
- `scripts/setup_database.py` - Populate database with sample data
- `scripts/db_status.py` - Check current database status
- `scripts/check_users.py` - List all user accounts

## Default Login Credentials

After setup, you can log in with any of these accounts:

| Username | Password | Email |
|----------|----------|-------|
| admin | admin123 | admin@plottwist.com |
| manager1 | admin123 | manager1@plottwist.com |
| manager2 | admin123 | manager2@plottwist.com |
| supervisor | admin123 | supervisor@plottwist.com |

## What's Included

### Sample Books (15 titles)
- Classic literature (To Kill a Mockingbird, 1984, Pride and Prejudice)
- Modern bestsellers (Where the Crawdads Sing, Atomic Habits)
- Popular fiction (The Hobbit, The Fault in Our Stars)
- Non-fiction (Sapiens, A Brief History of Time)

### Sample Orders (15 orders)
- Various customer names and addresses
- Different order statuses (Pending, Processing, Shipped, Completed)
- Random quantities and timestamps

### Admin Features
- User management with email notifications
- Order processing and status updates
- Inventory management (add/edit/delete books)
- CSV import/export functionality
- Two-factor authentication

## Manual Commands

If you prefer to run things manually:

```bash
# Check database status
python scripts/db_status.py

# Setup sample data
python scripts/setup_database.py

# Start the application
python app/app.py
```

## Access Your Bookstore

Once started, visit: **http://127.0.0.1:5000**

The system includes:
- Admin dashboard with inventory and order management
- Customer browsing interface
- Shopping cart functionality
- Email notifications for orders
- Two-factor authentication for security