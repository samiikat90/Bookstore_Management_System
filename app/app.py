## Application entrypoint and main Flask app configuration.
##
## This file contains the Flask app, database models (Book, User, Purchase),
## authentication (Flask-Login) and manager-only routes for inventory and
## purchase review. Comments explain the purpose of each section.
from flask import Flask, request, render_template, redirect, url_for, flash, jsonify, make_response, session, Response
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from functools import wraps
from sqlalchemy import text, union_all, or_
from io import StringIO
import os, json
import csv
import random
import string
import smtplib
from payment_utils import validate_payment_method, process_payment, handle_payment_error, detect_card_type
from payment_utils import PaymentError, CardDeclinedError, InvalidPaymentMethodError, InsufficientFundsError, NetworkTimeoutError
from encryption_utils import DataEncryption

# Initialize Flask app
app = Flask(__name__, instance_relative_config=True)
app.secret_key = 'your_secret_key'

# Configure session to expire when browser closes
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)  # Fallback timeout
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Security: prevent JavaScript access to session cookie
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # CSRF protection

# Auto-logout configuration for admin inactivity
ADMIN_SESSION_TIMEOUT = timedelta(minutes=10)  # 10 minutes of inactivity
SESSION_WARNING_TIME = timedelta(minutes=8)    # Show warning at 8 minutes

# Disable CSRF protection for development (this might be causing API issues)
app.config['WTF_CSRF_ENABLED'] = False

# Force the instance path to be relative to this app.py file location
app.instance_path = os.path.join(os.path.dirname(__file__), '..', 'instance')

# Ensure instance folder exists
os.makedirs(app.instance_path, exist_ok=True)

# Configure file upload to use instance/uploads
app.config['UPLOAD_FOLDER'] = os.path.join(app.instance_path, 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024
ALLOWED_EXTENSIONS = {'csv'}

# Configure SQLAlchemy to use DB inside instance
db_path = os.path.join(app.instance_path, 'inventory.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# =============================
# DISCOUNT CODE CONFIGURATION
# =============================
# Discount code database (code: [discount rate, minimum order amount])
DISCOUNT_CODES = {
    'SAVE10': [0.10, 30.0],   # 10% off orders over $30
    'BOOK20': [0.20, 50.0],   # 20% off orders over $50
    'FALL25': [0.25, 100.0],  # 25% off orders over $100
    'STUDENT15': [0.15, 25.0], # 15% off orders over $25
    'WINTER30': [0.30, 75.0]   # 30% off orders over $75
}

# =============================
# BOOK GENRE CONFIGURATION
# =============================
# Predefined book genres available in the catalog
BOOK_GENRES = [
    'Fiction',
    'Mystery',
    'Romance', 
    'Science Fiction',
    'Fantasy',
    'Biography',
    'History',
    'Self-Help',
    'Horror',
    'Thriller',
    'Adventure',
    'Children',
    'Young Adult',
    'Poetry',
    'Drama',
    'Philosophy',
    'Psychology',
    'Business',
    'Health & Wellness',
    'Travel'
]

# Initialize encryption for sensitive data
encryption = DataEncryption()

# Flask-Login setup
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

# Define Book model
class Book(db.Model):
    isbn = db.Column(db.String(20), primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, default=0)
    in_stock = db.Column(db.Boolean, default=True)
    cover_type = db.Column(db.String(50))
    description = db.Column(db.Text)
    genre = db.Column(db.String(100), nullable=True)  # New field for notifications


# Simple User model for manager authentication
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), nullable=True)  # Email for notifications
    full_name = db.Column(db.String(100), nullable=True)  # Full name for notifications
    # keep both fields for compatibility with older DBs that used `password`
    password_hash = db.Column(db.String(128), nullable=True)
    password = db.Column(db.String(128), nullable=True)
    is_manager = db.Column(db.Boolean, default=False)
    receive_notifications = db.Column(db.Boolean, default=True)  # Whether to receive email notifications
    
    # Two-Factor Authentication fields
    two_fa_code = db.Column(db.String(10), nullable=True)  # Current 2FA code
    two_fa_expires = db.Column(db.DateTime, nullable=True)  # When the code expires
    two_fa_verified = db.Column(db.Boolean, default=False)  # Whether 2FA was completed for current session

    # Password Reset fields
    reset_token = db.Column(db.String(100), nullable=True)  # Password reset token
    reset_token_expires = db.Column(db.DateTime, nullable=True)  # When the reset token expires

    def set_password(self, password):
        hashed = generate_password_hash(password)
        self.password_hash = hashed
        # also populate legacy `password` column so older schemas accept inserts
        self.password = hashed

    def check_password(self, password):
        if self.password_hash:
            return check_password_hash(self.password_hash, password)
        if self.password:
            # fallback for legacy stored hashes
            return check_password_hash(self.password, password)
        return False

    def generate_2fa_code(self):
        """Generate a new 6-digit 2FA code and set expiration time."""
        code = ''.join(random.choices(string.digits, k=6))
        self.two_fa_code = code
        self.two_fa_expires = datetime.now() + timedelta(minutes=10)  # Code expires in 10 minutes
        self.two_fa_verified = False
        return code

    def verify_2fa_code(self, code):
        """Verify the provided 2FA code."""
        if not self.two_fa_code or not self.two_fa_expires:
            return False
        
        # Check if code has expired
        if datetime.now() > self.two_fa_expires:
            self.clear_2fa_code()
            return False
        
        # Check if code matches
        if self.two_fa_code == code:
            self.two_fa_verified = True
            self.clear_2fa_code()
            return True
        
        return False

    def clear_2fa_code(self):
        """Clear the 2FA code and expiration."""
        self.two_fa_code = None
        self.two_fa_expires = None

    def generate_reset_token(self):
        """Generate a password reset token that expires in 1 hour."""
        self.reset_token = ''.join(random.choices(string.ascii_letters + string.digits, k=64))
        self.reset_token_expires = datetime.now() + timedelta(hours=1)
        return self.reset_token

    def verify_reset_token(self, token):
        """Verify if the provided token is valid and not expired."""
        if not self.reset_token or not self.reset_token_expires:
            return False
        
        # Check if token has expired
        if datetime.now() > self.reset_token_expires:
            self.clear_reset_token()
            return False
        
        # Check if token matches
        return self.reset_token == token

    def clear_reset_token(self):
        """Clear the reset token and expiration."""
        self.reset_token = None
        self.reset_token_expires = None


# Customer model for customer registration and login
class Customer(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email_encrypted = db.Column(db.Text, nullable=False)  # Encrypted email storage
    password_hash = db.Column(db.String(128), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    phone_encrypted = db.Column(db.Text, nullable=True)  # Encrypted phone storage
    
    # Address fields - encrypted
    address_encrypted = db.Column(db.Text, nullable=True)  # Keep for backward compatibility
    address_line1_encrypted = db.Column(db.Text, nullable=True)
    address_line2_encrypted = db.Column(db.Text, nullable=True)
    city = db.Column(db.String(100), nullable=True)  # City can remain unencrypted
    state = db.Column(db.String(50), nullable=True)  # State can remain unencrypted
    zip_code = db.Column(db.String(20), nullable=True)  # Zip can remain unencrypted
    
    date_registered = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Customer preferences
    receive_marketing = db.Column(db.Boolean, default=False)
    
    # Password Reset fields
    reset_token = db.Column(db.String(100), nullable=True)  # Password reset token
    reset_token_expires = db.Column(db.DateTime, nullable=True)  # When the reset token expires
    
    # Properties for transparent encryption/decryption
    @property
    def email(self):
        """Decrypt and return email address."""
        if self.email_encrypted:
            return encryption.decrypt(self.email_encrypted)
        return None
    
    @email.setter
    def email(self, value):
        """Encrypt and store email address."""
        if value:
            self.email_encrypted = encryption.encrypt(value)
        else:
            self.email_encrypted = None
    
    @property
    def phone(self):
        """Decrypt and return phone number."""
        if self.phone_encrypted:
            return encryption.decrypt(self.phone_encrypted)
        return None
    
    @phone.setter
    def phone(self, value):
        """Encrypt and store phone number."""
        if value:
            self.phone_encrypted = encryption.encrypt(value)
        else:
            self.phone_encrypted = None
    
    @property
    def address(self):
        """Decrypt and return address."""
        if self.address_encrypted:
            return encryption.decrypt(self.address_encrypted)
        return None
    
    @address.setter
    def address(self, value):
        """Encrypt and store address."""
        if value:
            self.address_encrypted = encryption.encrypt(value)
        else:
            self.address_encrypted = None
    
    @property
    def address_line1(self):
        """Decrypt and return address line 1."""
        if self.address_line1_encrypted:
            return encryption.decrypt(self.address_line1_encrypted)
        return None
    
    @address_line1.setter
    def address_line1(self, value):
        """Encrypt and store address line 1."""
        if value:
            self.address_line1_encrypted = encryption.encrypt(value)
        else:
            self.address_line1_encrypted = None
    
    @property
    def address_line2(self):
        """Decrypt and return address line 2."""
        if self.address_line2_encrypted:
            return encryption.decrypt(self.address_line2_encrypted)
        return None
    
    @address_line2.setter
    def address_line2(self, value):
        """Encrypt and store address line 2."""
        if value:
            self.address_line2_encrypted = encryption.encrypt(value)
        else:
            self.address_line2_encrypted = None
    
    def set_password(self, password):
        """Set password hash for customer."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check if provided password matches stored hash."""
        return check_password_hash(self.password_hash, password)
    
    def get_id(self):
        """Return customer ID for Flask-Login."""
        return f"customer_{self.id}"
    
    @property
    def is_manager(self):
        """Customers are never managers."""
        return False

    def generate_reset_token(self):
        """Generate a password reset token that expires in 1 hour."""
        self.reset_token = ''.join(random.choices(string.ascii_letters + string.digits, k=64))
        self.reset_token_expires = datetime.now() + timedelta(hours=1)
        return self.reset_token

    def verify_reset_token(self, token):
        """Verify if the provided token is valid and not expired."""
        if not self.reset_token or not self.reset_token_expires:
            return False
        
        # Check if token has expired
        if datetime.now() > self.reset_token_expires:
            self.clear_reset_token()
            return False
        
        # Check if token matches
        return self.reset_token == token

    def clear_reset_token(self):
        """Clear the reset token and expiration."""
        self.reset_token = None
        self.reset_token_expires = None
    
    def __repr__(self):
        return f'<Customer {self.username}>'


    # Orders / Purchases model
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(120), nullable=False)
    customer_email = db.Column(db.String(120))
    customer_phone = db.Column(db.String(50))
    customer_address = db.Column(db.Text)
    book_isbn = db.Column(db.String(50))
    quantity = db.Column(db.Integer, default=1)
    status = db.Column(db.String(50), default='Pending')
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    customer_id = db.Column(db.Integer, default=1)  # required by legacy schema


# New safe Purchase model stored in table 'purchases' to avoid touching legacy 'order' table
class Purchase(db.Model):
    __tablename__ = 'purchases'
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(120), nullable=False)
    customer_email_encrypted = db.Column(db.Text)  # Encrypted email storage
    customer_phone_encrypted = db.Column(db.Text)  # Encrypted phone storage
    customer_address_encrypted = db.Column(db.Text)  # Encrypted address storage
    book_isbn = db.Column(db.String(50))
    quantity = db.Column(db.Integer, default=1)
    status = db.Column(db.String(50), default='Pending')
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    source = db.Column(db.String(20), default='purchase')  # indicate this is from purchases table
    
    # Properties for transparent encryption/decryption
    @property
    def customer_email(self):
        """Decrypt and return customer email."""
        if self.customer_email_encrypted:
            return encryption.decrypt(self.customer_email_encrypted)
        return None
    
    @customer_email.setter
    def customer_email(self, value):
        """Encrypt and store customer email."""
        if value:
            self.customer_email_encrypted = encryption.encrypt(value)
        else:
            self.customer_email_encrypted = None
    
    @property
    def customer_phone(self):
        """Decrypt and return customer phone."""
        if self.customer_phone_encrypted:
            return encryption.decrypt(self.customer_phone_encrypted)
        return None
    
    @customer_phone.setter
    def customer_phone(self, value):
        """Encrypt and store customer phone."""
        if value:
            self.customer_phone_encrypted = encryption.encrypt(value)
        else:
            self.customer_phone_encrypted = None
    
    @property
    def customer_address(self):
        """Decrypt and return customer address."""
        if self.customer_address_encrypted:
            return encryption.decrypt(self.customer_address_encrypted)
        return None
    
    @customer_address.setter
    def customer_address(self, value):
        """Encrypt and store customer address."""
        if value:
            self.customer_address_encrypted = encryption.encrypt(value)
        else:
            self.customer_address_encrypted = None
    
    # Status options
    STATUS_OPTIONS = [
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Processing', 'Processing'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled')
    ]
    
    def get_status_badge_class(self):
        """Return Bootstrap badge class for status display."""
        status_classes = {
            'Pending': 'badge-warning',
            'Confirmed': 'badge-info',
            'Processing': 'badge-primary',
            'Shipped': 'badge-success',
            'Delivered': 'badge-success',
            'Cancelled': 'badge-danger'
        }
        return status_classes.get(self.status, 'badge-secondary')
    
    def get_status_icon(self):
        """Return FontAwesome icon for status display."""
        status_icons = {
            'Pending': 'fas fa-clock',
            'Confirmed': 'fas fa-check-circle',
            'Processing': 'fas fa-cog',
            'Shipped': 'fas fa-truck',
            'Delivered': 'fas fa-home',
            'Cancelled': 'fas fa-times-circle'
        }
        return status_icons.get(self.status, 'fas fa-question-circle')

# Sale model for customer shopping cart purchases
class Sale(db.Model):
    __tablename__ = 'sales'
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.String(50), nullable=False)  # ISBN of the book
    quantity = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


# Payment Method Model
class PaymentMethod(db.Model):
    """Stores payment method information for transactions."""
    __tablename__ = 'payment_methods'
    id = db.Column(db.Integer, primary_key=True)
    purchase_id = db.Column(db.Integer, db.ForeignKey('purchases.id'), nullable=True)
    method_type = db.Column(db.String(20), nullable=False)  # credit_card, paypal, bank_transfer
    
    # Credit Card fields
    card_last_four = db.Column(db.String(4), nullable=True)
    card_type = db.Column(db.String(20), nullable=True)  # Visa, Mastercard, etc.
    cardholder_name = db.Column(db.String(100), nullable=True)
    
    # PayPal fields - encrypted
    paypal_email_encrypted = db.Column(db.Text, nullable=True)
    
    # Bank Transfer fields
    bank_name = db.Column(db.String(100), nullable=True)
    account_last_four = db.Column(db.String(4), nullable=True)
    
    # General fields
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), default='USD')
    transaction_id = db.Column(db.String(100), nullable=True)
    status = db.Column(db.String(20), default='pending')  # pending, completed, failed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Property for transparent encryption/decryption of PayPal email
    @property
    def paypal_email(self):
        """Decrypt and return PayPal email."""
        if self.paypal_email_encrypted:
            return encryption.decrypt(self.paypal_email_encrypted)
        return None
    
    @paypal_email.setter
    def paypal_email(self, value):
        """Encrypt and store PayPal email."""
        if value:
            self.paypal_email_encrypted = encryption.encrypt(value)
        else:
            self.paypal_email_encrypted = None
    
    def __repr__(self):
        return f'<PaymentMethod {self.method_type}: ${self.amount}>'


# Notification Preference Models
class BookNotification(db.Model):
    """Tracks customer notifications for specific book titles."""
    __tablename__ = 'book_notifications'
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    book_title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    customer = db.relationship('Customer', backref='book_notifications')
    
    def __repr__(self):
        return f'<BookNotification {self.customer_id}: {self.book_title}>'


class GenreNotification(db.Model):
    """Tracks customer notifications for specific genres."""
    __tablename__ = 'genre_notifications'
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    genre = db.Column(db.String(100), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    customer = db.relationship('Customer', backref='genre_notifications')
    
    def __repr__(self):
        return f'<GenreNotification {self.customer_id}: {self.genre}>'


class NotificationLog(db.Model):
    """Logs notifications sent to customers."""
    __tablename__ = 'notification_logs'
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    notification_type = db.Column(db.String(50), nullable=False)  # 'book' or 'genre'
    book_title = db.Column(db.String(200), nullable=True)
    genre = db.Column(db.String(100), nullable=True)
    message = db.Column(db.Text, nullable=False)
    sent_date = db.Column(db.DateTime, default=datetime.utcnow)
    email_sent = db.Column(db.Boolean, default=False)
    
    # Relationship
    customer = db.relationship('Customer', backref='notification_logs')
    
    def __repr__(self):
        return f'<NotificationLog {self.customer_id}: {self.notification_type}>'


@login_manager.user_loader
def load_user(user_id):
    try:
        # Handle both admin users and customers
        if user_id.startswith('customer_'):
            customer_id = int(user_id.split('_')[1])
            return Customer.query.get(customer_id)
        else:
            # Legacy admin user
            return User.query.get(int(user_id))
    except Exception:
        return None


@login_manager.unauthorized_handler
def unauthorized():
    # Check if this is an API request
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Authentication required', 'redirect': url_for('login')}), 401
    # For regular requests, redirect to login
    return redirect(url_for('login'))


def manager_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        if not getattr(current_user, 'is_manager', False):
            flash('Manager access required', 'danger')
            return redirect(url_for('login'))
        
        # Check for session timeout
        if check_session_timeout():
            logout_user()
            session.pop('last_activity', None)
            flash('Your session has expired due to inactivity. Please login again.', 'warning')
            return redirect(url_for('login'))
        
        # Update last activity for session timeout tracking
        session['last_activity'] = datetime.utcnow().isoformat()
        
        return func(*args, **kwargs)
    return wrapper


def check_session_timeout():
    """Check if admin session has timed out due to inactivity."""
    if current_user.is_authenticated and current_user.is_manager:
        last_activity_str = session.get('last_activity')
        if last_activity_str:
            try:
                last_activity = datetime.fromisoformat(last_activity_str)
                if datetime.utcnow() - last_activity > ADMIN_SESSION_TIMEOUT:
                    return True
            except (ValueError, TypeError):
                # If we can't parse the timestamp, consider it timed out
                return True
    return False


def timeout_required(func):
    """Custom decorator that checks for session timeout on admin routes."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if check_session_timeout():
            logout_user()
            session.pop('last_activity', None)
            flash('Your session has expired due to inactivity. Please login again.', 'warning')
            return redirect(url_for('login'))
        
        # Update last activity
        if current_user.is_authenticated and current_user.is_manager:
            session['last_activity'] = datetime.utcnow().isoformat()
        
        return func(*args, **kwargs)
    return wrapper

# Helper function
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Notification functions
def send_admin_notification(subject, message, order_details=None):
    """Send email notification to all admin users who have notifications enabled."""
    try:
        # Get all admin users with notifications enabled
        admin_users = User.query.filter_by(is_manager=True, receive_notifications=True).all()
        
        if not admin_users:
            print("No admin users with notifications enabled found")
            return
        
        # Prepare email content
        if order_details:
            body = f"{message}\n\n--- Order Details ---\n"
            body += f"Order ID: {order_details.get('id', 'N/A')}\n"
            body += f"Customer: {order_details.get('customer_name', 'N/A')}\n"
            body += f"Email: {order_details.get('customer_email', 'N/A')}\n"
            body += f"Phone: {order_details.get('customer_phone', 'N/A')}\n"
            body += f"Book ISBN: {order_details.get('book_isbn', 'N/A')}\n"
            body += f"Quantity: {order_details.get('quantity', 'N/A')}\n"
            body += f"Status: {order_details.get('status', 'N/A')}\n"
            body += f"Date: {order_details.get('timestamp', 'N/A')}\n"
        else:
            body = message
        
        body += f"\n\nView the admin dashboard: http://127.0.0.1:5000/admin\n\nBest regards,\nChapter 6: A Plot Twist Bookstore System"
        
        # Send email to each admin
        for admin in admin_users:
            if not admin.email:
                print(f"Skipping {admin.username} - no email address configured")
                continue
                
            try:
                msg = MIMEText(body)
                msg['Subject'] = subject
                msg['From'] = os.environ.get('GMAIL_EMAIL', 'chapter6aplottwist@gmail.com')
                msg['To'] = admin.email
                
                smtp = smtplib.SMTP('smtp.gmail.com', 587)
                smtp.starttls()
                smtp.login(os.environ.get('GMAIL_EMAIL', 'chapter6aplottwist@gmail.com'), 
                          os.environ.get('GMAIL_APP_PASSWORD', 'giuw lmir sdmo fgej'))
                smtp.sendmail(os.environ.get('GMAIL_EMAIL', 'chapter6aplottwist@gmail.com'), 
                             [admin.email], msg.as_string())
                smtp.quit()
                print(f"Notification sent to {admin.full_name or admin.username} ({admin.email})")
                
            except Exception as e:
                print(f"Failed to send notification to {admin.email}: {e}")
                
    except Exception as e:
        print(f"Error sending admin notifications: {e}")


def send_customer_purchase_notification(customer_email, customer_name, purchase_details, transaction_id, discount_info=None):
    """Send purchase confirmation email to customer."""
    try:
        subject = "Order Confirmation - Chapter 6: A Plot Twist Bookstore"
        
        # Build order summary
        order_summary = ""
        subtotal = 0
        for item in purchase_details:
            book_title = item.get('title', 'Unknown Book')
            quantity = item.get('quantity', 1)
            price = item.get('price', 0)
            item_total = price * quantity
            subtotal += item_total
            order_summary += f"• {book_title} (Qty: {quantity}) - ${price:.2f} each = ${item_total:.2f}\n"
        
        # Calculate discount and final total
        discount_text = ""
        final_total = subtotal
        if discount_info:
            discount_code = discount_info.get('code')
            discount_amount = discount_info.get('amount', 0)
            final_total = discount_info.get('final_total', subtotal)
            if discount_code and discount_amount > 0:
                discount_text = f"\nSubtotal: ${subtotal:.2f}\nDiscount ({discount_code}): -${discount_amount:.2f}"
        
        total_text = f"TOTAL: ${final_total:.2f}"
        if discount_text:
            total_text = f"{discount_text}\n{total_text}"
        
        body = f"""Dear {customer_name},

Thank you for your purchase from Chapter 6: A Plot Twist Bookstore!

Your order has been confirmed and is being processed.

ORDER DETAILS:
Transaction ID: {transaction_id}
Order Date: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}

ITEMS ORDERED:
{order_summary}
{total_text}

Your order status can be tracked by logging into your account at:
http://127.0.0.1:5000/customer_login

We'll send you another notification when your order ships.

Thank you for choosing Chapter 6: A Plot Twist Bookstore!

Best regards,
The Chapter 6 Team
Email: chapter6aplottwist@gmail.com
"""
        
        # Send email
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = os.environ.get('GMAIL_EMAIL', 'chapter6aplottwist@gmail.com')
        msg['To'] = customer_email
        
        smtp = smtplib.SMTP('smtp.gmail.com', 587)
        smtp.starttls()
        smtp.login(os.environ.get('GMAIL_EMAIL', 'chapter6aplottwist@gmail.com'), 
                  os.environ.get('GMAIL_APP_PASSWORD', 'giuw lmir sdmo fgej'))
        smtp.sendmail(os.environ.get('GMAIL_EMAIL', 'chapter6aplottwist@gmail.com'), 
                     [customer_email], msg.as_string())
        smtp.quit()
        
        print(f"Purchase confirmation sent to {customer_name} ({customer_email})")
        return True
        
    except Exception as e:
        print(f"Failed to send purchase confirmation to {customer_email}: {e}")
        return False


def send_2fa_code(user):
    """Send 2FA code to user's email."""
    if not user.email:
        print(f"No email configured for user {user.username}")
        return False
    
    try:
        # Generate and save 2FA code
        code = user.generate_2fa_code()
        db.session.commit()
        
        # Prepare email content
        subject = "Your Security Code - Chapter 6: A Plot Twist"
        body = f"""Hello {user.full_name or user.username},

Your security code for logging into the Chapter 6: A Plot Twist admin system is:

{code}

This code will expire in 10 minutes for security purposes.

If you did not request this code, please contact your system administrator immediately.

Best regards,
Chapter 6: A Plot Twist Security System"""

        # Send email
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = os.environ.get('GMAIL_EMAIL', 'chapter6aplottwist@gmail.com')
        msg['To'] = user.email
        
        smtp = smtplib.SMTP('smtp.gmail.com', 587)
        smtp.starttls()
        smtp.login(os.environ.get('GMAIL_EMAIL', 'chapter6aplottwist@gmail.com'), 
                  os.environ.get('GMAIL_APP_PASSWORD', 'giuw lmir sdmo fgej'))
        smtp.sendmail(os.environ.get('GMAIL_EMAIL', 'chapter6aplottwist@gmail.com'), 
                     [user.email], msg.as_string())
        smtp.quit()
        
        print(f"2FA code sent to {user.email}")
        return True
        
    except Exception as e:
        print(f"Failed to send 2FA code to {user.email}: {e}")
        return False


def send_password_reset_email(email, reset_token, is_customer=False):
    """Send password reset email with reset link."""
    try:
        # Determine the correct reset URL based on user type
        if is_customer:
            reset_url = f"http://127.0.0.1:5000/customer/reset-password/{reset_token}"
            portal_name = "Customer Portal"
        else:
            reset_url = f"http://127.0.0.1:5000/reset-password/{reset_token}"
            portal_name = "Admin Portal"
        
        subject = f"Password Reset Request - {portal_name}"
        
        body = f"""Hello,

You have requested to reset your password for the Chapter 6: A Plot Twist {portal_name}.

To reset your password, please click the link below:

{reset_url}

This link will expire in 1 hour for security reasons.

If you did not request this password reset, please ignore this email. Your password will remain unchanged.

Best regards,
Chapter 6: A Plot Twist Security Team"""

        # Send email
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = os.environ.get('GMAIL_EMAIL', 'chapter6aplottwist@gmail.com')
        msg['To'] = email
        
        smtp = smtplib.SMTP('smtp.gmail.com', 587)
        smtp.starttls()
        smtp.login(os.environ.get('GMAIL_EMAIL', 'chapter6aplottwist@gmail.com'), 
                  os.environ.get('GMAIL_APP_PASSWORD', 'giuw lmir sdmo fgej'))
        smtp.sendmail(os.environ.get('GMAIL_EMAIL', 'chapter6aplottwist@gmail.com'), 
                     [email], msg.as_string())
        smtp.quit()
        
        print(f"Password reset email sent to {email}")
        return True
        
    except Exception as e:
        print(f"Failed to send password reset email to {email}: {e}")
        return False


def get_order_details_dict(purchase):
    """Convert a Purchase object to a dictionary for notifications."""
    return {
        'id': purchase.id,
        'customer_name': purchase.customer_name,
        'customer_email': purchase.customer_email,
        'customer_phone': purchase.customer_phone,
        'book_isbn': purchase.book_isbn,
        'quantity': purchase.quantity,
        'status': purchase.status,
        'timestamp': purchase.timestamp.strftime('%Y-%m-%d %H:%M:%S') if purchase.timestamp else 'N/A'
    }

# --- CSV Catalog Browser Integration ---
def load_catalog(file_path):
    """Load catalog data from a CSV file."""
    catalog = []
    try:
        with open(file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Defensive: ensure keys exist and price is float
                item = {
                    'Name': row.get('Name', 'Unknown'),
                    'Category': row.get('Category', 'Uncategorized'),
                    'Price': float(row.get('Price', 0))
                }
                catalog.append(item)
    except FileNotFoundError:
        print("Error: Catalog file not found.")
    except Exception as e:
        print(f"Error loading catalog: {e}")
    return catalog

@app.route('/catalog')
def catalog_view():
    """Enhanced catalog view with proper genre filtering and search."""
    # Get search and filter parameters
    search = (request.args.get('search') or '').strip()
    genre = (request.args.get('genre') or '').strip()
    sort = request.args.get('sort', 'title')
    
    # Load books from database inventory
    books_query = Book.query.filter(Book.quantity > 0)  # Only show books in stock
    
    # Apply search filter
    if search:
        books_query = books_query.filter(
            db.or_(
                Book.title.contains(search),
                Book.author.contains(search),
                Book.description.contains(search)
            )
        )
    
    # Apply genre filter
    if genre:
        books_query = books_query.filter(Book.genre == genre)
    
    # Apply sorting
    if sort == 'title':
        books_query = books_query.order_by(Book.title.asc())
    elif sort == 'author':
        books_query = books_query.order_by(Book.author.asc())
    elif sort == 'price':
        books_query = books_query.order_by(Book.price.asc())
    elif sort == 'genre':
        books_query = books_query.order_by(Book.genre.asc())
    else:
        books_query = books_query.order_by(Book.title.asc())
    
    books = books_query.all()
    
    # Get available genres from books in stock and predefined genres
    available_genres = set()
    for book in Book.query.filter(Book.quantity > 0).all():
        if book.genre:
            available_genres.add(book.genre)
    
    # Add predefined genres that might not be in current inventory
    for predefined_genre in BOOK_GENRES:
        available_genres.add(predefined_genre)
    
    available_genres = sorted(list(available_genres))
    
    return render_template('catalog.html', 
                         books=books, 
                         search=search, 
                         genre=genre,
                         sort=sort,
                         genres=available_genres,
                         total_books=len(books),
                         predefined_genres=BOOK_GENRES)


@app.route('/inventory')
@login_required
@manager_required
def inventory():
    """Inventory management page with CSV upload/export functionality."""
    search = (request.args.get('search') or '').strip()
    category = (request.args.get('category') or '').strip()
    
    # Get all books from database
    books_query = Book.query
    
    if search:
        books_query = books_query.filter(Book.title.contains(search))
    
    if category:
        books_query = books_query.filter(Book.cover_type == category)
    
    books = books_query.all()
    categories = sorted(set(book.cover_type for book in Book.query.all() if book.cover_type))
    
    return render_template('inventory.html', books=books, search=search, category=category, categories=categories)


@app.route('/orders')
@login_required
@manager_required
def orders_view():
    orders = Order.query.order_by(Order.timestamp.desc()).all()
    return render_template('orders.html', orders=orders)


@app.route('/orders/update/<int:order_id>', methods=['POST'])
@login_required
@manager_required
def update_order(order_id):
    order = Purchase.query.get(order_id)
    if not order:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify(success=False, message='Order not found'), 404
        flash('Order not found', 'danger')
        return redirect(url_for('orders_view'))
    
    old_status = order.status
    new_status = request.form.get('status')
    
    if new_status and old_status != new_status:
        order.status = new_status
        db.session.commit()
        
        # Send notification for status change
        try:
            order_details = get_order_details_dict(order)
            send_admin_notification(
                subject=f"Order Status Updated - Chapter 6: A Plot Twist",
                message=f"Order #{order.id} status changed from '{old_status}' to '{new_status}' by {current_user.username}.",
                order_details=order_details
            )
        except Exception as e:
            print(f"Error sending status change notification: {e}")
        
        # If this was an AJAX request, respond with JSON so the client can update without a full redirect
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify(success=True, message='Order updated')
        flash('Order updated', 'success')
    return redirect(url_for('orders_view'))


@app.route('/purchases')
@login_required
@manager_required
def purchases_view():
    purchases = Purchase.query.order_by(Purchase.timestamp.desc()).all()
    return render_template('purchases.html', purchases=purchases)


@app.route('/purchases/update/<int:purchase_id>', methods=['POST'])
@login_required
@manager_required
def update_purchase(purchase_id):
    p = Purchase.query.get(purchase_id)
    if not p:
        flash('Purchase not found', 'danger')
        return redirect(url_for('purchases_view'))
    
    old_status = p.status
    new_status = request.form.get('status')
    
    if new_status and old_status != new_status:
        p.status = new_status
        db.session.commit()
        
        # Send notification for status change
        try:
            order_details = get_order_details_dict(p)
            send_admin_notification(
                subject=f"Purchase Status Updated - Chapter 6: A Plot Twist",
                message=f"Purchase #{p.id} status changed from '{old_status}' to '{new_status}' by {current_user.username}.",
                order_details=order_details
            )
        except Exception as e:
            print(f"Error sending status change notification: {e}")
        
        flash('Purchase updated', 'success')
    return redirect(url_for('purchases_view'))


@app.route('/purchases/<int:purchase_id>')
@login_required
@manager_required
def purchase_detail(purchase_id):
    p = Purchase.query.get_or_404(purchase_id)
    return render_template('purchase_detail.html', p=p)


@app.route('/purchases/export.csv')
@login_required
@manager_required
def export_purchases_csv():
    import csv
    from io import StringIO
    si = StringIO()
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    status = request.args.get('status')

    query = Purchase.query.order_by(Purchase.id)
    if start_date:
        query = query.filter(Purchase.timestamp >= datetime.strptime(start_date, '%Y-%m-%d'))
    if end_date:
        query = query.filter(Purchase.timestamp <= datetime.strptime(end_date, '%Y-%m-%d'))
    if status:
        query = query.filter(Purchase.status == status)

    writer = csv.writer(si)
    writer.writerow(['id','source','customer_name','customer_email','customer_phone','customer_address','book_isbn','quantity','status','timestamp'])
    for p in query.all():
        writer.writerow([p.id,'purchase',p.customer_name,p.customer_email,p.customer_phone,p.customer_address,p.book_isbn,p.quantity,p.status,p.timestamp])

    # Format the filename to include any filters
    filename = 'purchases'
    if start_date and end_date:
        filename += f'_{start_date}_to_{end_date}'
    if status:
        filename += f'_{status}'
    filename += '.csv'

    output = si.getvalue()
    return app.response_class(output, mimetype='text/csv', headers={'Content-Disposition':f'attachment;filename={filename}'})


# Public route to create a purchase (simulate customer action)
@app.route('/create_purchase', methods=['GET', 'POST'])
def create_purchase():
    if 'cart' not in session:
        session['cart'] = []
    cart = session['cart']
    # Persist user info in session
    user_info_keys = ['customer_name', 'customer_email', 'customer_phone', 'customer_address']
    if 'user_info' not in session:
        session['user_info'] = {k: '' for k in user_info_keys}
    user_info = session['user_info']
    if request.method == 'POST':
        # Update session user info from form
        for k in user_info_keys:
            v = request.form.get(k)
            if v:
                user_info[k] = v
        session['user_info'] = user_info
        name = user_info['customer_name']
        email = user_info['customer_email']
        phone = user_info['customer_phone']
        address = user_info['customer_address']
        isbn = request.form.get('book_isbn') or request.form.get('catalog_isbn')
        qty = int(request.form.get('quantity') or 1)
        book = Book.query.get(isbn) if isbn else None
        # Add to cart (dedupe by ISBN)
        if request.form.get('add_to_cart'):
            added = False
            if isbn:
                for item in cart:
                    if item.get('isbn') == isbn:
                        item['quantity'] = item.get('quantity', 0) + qty
                        added = True
                        break
            if not added:
                if book:
                    cart.append({'isbn': book.isbn, 'title': book.title, 'author': book.author, 'price': book.price, 'quantity': qty})
                else:
                    cart.append({'isbn': isbn, 'title': 'Unknown', 'author': '', 'price': 0, 'quantity': qty})
            session['cart'] = cart
            flash('Book added to cart.', 'info')
            return redirect(url_for('create_purchase'))
        # Checkout
        elif request.form.get('checkout'):
            if not cart:
                flash('Cart is empty.', 'danger')
                return redirect(url_for('create_purchase'))
            total = 0
            book_lines = []
            created_purchases = []
            for item in cart:
                p = Purchase(customer_name=name, customer_email=email, customer_phone=phone, customer_address=address, book_isbn=item['isbn'], quantity=item['quantity'])
                db.session.add(p)
                created_purchases.append(p)
                total += item['price'] * item['quantity']
                book_lines.append(f"- {item['title']} by {item['author']} (x{item['quantity']}) - ${item['price'] * item['quantity']:.2f}")
            db.session.commit()
            
            # Send admin notifications for new orders
            try:
                for purchase in created_purchases:
                    order_details = get_order_details_dict(purchase)
                    send_admin_notification(
                        subject="New Order Received - Chapter 6: A Plot Twist",
                        message=f"A new order has been placed by {name}.",
                        order_details=order_details
                    )
            except Exception as e:
                print(f"Error sending admin notifications: {e}")
            
            # Send confirmation email
            try:
                if email:
                    body = f"----- ORDER SUMMARY -----\nCustomer: {name}\nEmail: {email}\nAddress: {address}\n\nBooks Purchased:\n" + '\n'.join(book_lines) + f"\n\nTotal: ${total:.2f}\n\nThank you for your purchase!\n\nBest regards,\nChapter 6: A Plot Twist Bookstore"
                    msg = MIMEText(body)
                    msg['Subject'] = 'Your Order Confirmation - Chapter 6: A Plot Twist'
                    msg['From'] = os.environ.get('GMAIL_EMAIL', 'chapter6aplottwist@gmail.com')
                    msg['To'] = email
                    smtp = smtplib.SMTP('smtp.gmail.com', 587)
                    smtp.starttls()
                    smtp.login(os.environ.get('GMAIL_EMAIL', 'chapter6aplottwist@gmail.com'), os.environ.get('GMAIL_APP_PASSWORD', 'giuw lmir sdmo fgej'))
                    smtp.sendmail(os.environ.get('GMAIL_EMAIL', 'chapter6aplottwist@gmail.com'), [email], msg.as_string())
                    smtp.quit()
            except Exception as e:
                print(f"Error sending confirmation email: {e}")
            session['cart'] = []
            flash('Purchase completed. Confirmation email sent.', 'success')
            return redirect(url_for('create_purchase'))
    # Pass catalog and cart to template
    catalog = Book.query.filter_by(in_stock=True).all()
    return render_template('create_purchase.html', catalog=catalog, cart=cart, user_info=user_info)


@app.route('/cart/remove', methods=['POST'])
def cart_remove():
    isbn = request.form.get('remove_isbn')
    if 'cart' in session and isbn:
        new_cart = [item for item in session['cart'] if item.get('isbn') != isbn]
        session['cart'] = new_cart
        flash('Item removed from cart.', 'info')
    return redirect(url_for('create_purchase'))

# Homepage route - Public landing page
@app.route('/')
def index():
    """Public landing page with main navigation options"""
    return render_template('landing.html')

# Admin dashboard route
@app.route('/admin')
@login_required
@manager_required
def admin_dashboard():
    books = Book.query.all()
    orders = Purchase.query.order_by(Purchase.timestamp.desc()).all()
    # counts for badge and status breakdown
    pending_count = Purchase.query.filter_by(status='Pending').count()
    # status counts dict
    status_counts = {}
    for s in ['Pending', 'Processing', 'Shipped', 'Completed', 'Cancelled']:
        status_counts[s] = Purchase.query.filter_by(status=s).count()
    
    # Get recent admin users for dashboard display
    recent_admin_users = User.query.filter_by(is_manager=True).order_by(User.id.desc()).limit(5).all()
    
    return render_template('admin_dashboard.html', inventory=books, orders=orders, 
                         pending_count=pending_count, status_counts=status_counts, 
                         recent_admin_users=recent_admin_users)


@app.route('/orders/bulk_update', methods=['POST'])
@login_required
@manager_required
def orders_bulk_update():
    ids = request.form.getlist('selected')
    new_status = request.form.get('new_status')
    if not ids or not new_status:
        flash('No orders selected or no status provided.', 'danger')
        return redirect(url_for('admin_dashboard'))
    
    updated_orders = []
    try:
        for oid in ids:
            o = Purchase.query.get(int(oid))
            if o and o.status != new_status:
                old_status = o.status
                o.status = new_status
                updated_orders.append({
                    'order': o,
                    'old_status': old_status,
                    'new_status': new_status
                })
        
        db.session.commit()
        
        # Send notification for bulk status changes
        if updated_orders:
            try:
                order_list = []
                for update_info in updated_orders:
                    order_details = get_order_details_dict(update_info['order'])
                    order_list.append(f"Order #{update_info['order'].id}: {update_info['old_status']} -> {update_info['new_status']}")
                
                send_admin_notification(
                    subject=f"Bulk Order Status Update - Chapter 6: A Plot Twist",
                    message=f"Bulk update performed by {current_user.username}. {len(updated_orders)} orders updated to '{new_status}':\n\n" + "\n".join(order_list),
                    order_details=None  # For bulk updates, we'll include summary in the main message
                )
            except Exception as e:
                print(f"Error sending bulk update notification: {e}")
        
        flash(f'Updated {len(updated_orders)} orders to {new_status}.', 'success')
    except Exception as e:
        flash(f'Error updating orders: {e}', 'danger')
    return redirect(url_for('admin_dashboard'))


@app.route('/orders/export.csv')
@login_required
@manager_required
def export_orders_csv():
    import csv
    from io import StringIO
    si = StringIO()
    writer = csv.writer(si)
    writer.writerow(['id','customer_name','customer_email','customer_phone','customer_address','book_isbn','quantity','status','timestamp'])
    query = Purchase.query.order_by(Purchase.id)
    for o in query.all():
        writer.writerow([o.id, o.customer_name, o.customer_email, o.customer_phone, o.customer_address, o.book_isbn, o.quantity, o.status, o.timestamp])
    output = si.getvalue()
    return app.response_class(output, mimetype='text/csv', headers={'Content-Disposition':'attachment;filename=orders.csv'})

# Add book manually
@app.route('/add_book', methods=['GET', 'POST'])
@login_required
@manager_required
def add_book():
    if request.method == 'GET':
        # Show the add book form
        return render_template('add_book.html')
    
    try:
        isbn = request.form['isbn']
        title = request.form['title']
        author = request.form['author']
        price = float(request.form['price'])
        quantity = int(request.form.get('quantity', 0))
        cover_type = request.form.get('cover_type', '').strip()
        description = request.form.get('description', '').strip()

        new_book = Book(
            isbn=isbn,
            title=title,
            author=author,
            price=price,
            quantity=quantity,
            in_stock=quantity > 0,
            cover_type=cover_type,
            description=description
        )
        db.session.add(new_book)
        db.session.commit()
        flash(f"Book '{title}' added successfully!", 'success')
        return redirect(url_for('inventory'))
    except Exception as e:
        flash(f"Error adding book: {e}", 'danger')
        return redirect(url_for('add_book'))

    return redirect(url_for('inventory'))

# Edit book route
@app.route('/edit_book/<isbn>', methods=['GET', 'POST'])
@login_required
@manager_required
def edit_book(isbn):
    book = Book.query.get_or_404(isbn)
    
    if request.method == 'POST':
        try:
            book.title = request.form['title']
            book.author = request.form['author']
            book.price = float(request.form['price'])
            book.quantity = int(request.form.get('quantity', 0))
            book.cover_type = request.form.get('cover_type', '').strip()
            book.description = request.form.get('description', '').strip()
            book.in_stock = book.quantity > 0
            
            db.session.commit()
            flash(f"Book '{book.title}' updated successfully!", 'success')
            return redirect(url_for('inventory'))
        except Exception as e:
            flash(f"Error updating book: {e}", 'danger')
    
    return render_template('edit_book.html', book=book)

# Delete book route with quantity option
@app.route('/delete_book/<isbn>', methods=['POST'])
@login_required
@manager_required
def delete_book(isbn):
    try:
        book = Book.query.get_or_404(isbn)
        book_title = book.title
        current_quantity = book.quantity
        
        # Get the quantity to delete from form data
        quantity_to_delete = request.form.get('quantity_to_delete', type=int)
        
        # If no quantity specified, default to full deletion
        if quantity_to_delete is None:
            quantity_to_delete = current_quantity
        
        # Validate quantity
        if quantity_to_delete <= 0:
            flash(f"Invalid quantity. Please enter a positive number.", 'danger')
            return redirect(url_for('inventory'))
        
        if quantity_to_delete > current_quantity:
            flash(f"Cannot delete {quantity_to_delete} copies - only {current_quantity} available.", 'danger')
            return redirect(url_for('inventory'))
        
        # Check if there are any pending orders for this book
        pending_orders = Purchase.query.filter_by(book_isbn=isbn, status='Pending').count()
        if pending_orders > 0 and quantity_to_delete >= current_quantity:
            flash(f"Cannot delete all copies of '{book_title}' - there are {pending_orders} pending orders for this book. Please fulfill or cancel the orders first.", 'warning')
            return redirect(url_for('inventory'))
        
        # Determine action based on quantity
        if quantity_to_delete >= current_quantity:
            # Delete the entire book
            db.session.delete(book)
            flash(f"Book '{book_title}' has been completely removed from inventory.", 'success')
        else:
            # Reduce quantity
            book.quantity -= quantity_to_delete
            book.in_stock = book.quantity > 0
            flash(f"Removed {quantity_to_delete} copies of '{book_title}'. {book.quantity} copies remaining.", 'success')
        
        db.session.commit()
        
    except Exception as e:
        flash(f"Error processing deletion: {e}", 'danger')
        db.session.rollback()
    
    return redirect(url_for('inventory'))

# Mark book out of stock
@app.route('/mark_out_of_stock/<isbn>', methods=['POST'])
@login_required
@manager_required
def mark_out_of_stock(isbn):
    book = Book.query.filter_by(isbn=isbn).first()
    if book:
        book.in_stock = False
        book.quantity = 0
        db.session.commit()
        flash(f"Book '{book.title}' marked out of stock.", 'warning')
    return redirect(url_for('browse'))

# Download sample CSV template
@app.route('/download_sample_csv')
@login_required
@manager_required
def download_sample_csv():
    # Create a sample CSV content with proper ISBN formatting (quoted to prevent Excel conversion)
    csv_content = '''isbn,title,author,price,quantity,cover_type,description
"9780123456789",Sample Book Title,Sample Author,19.99,10,Paperback,This is a sample book description.
"9780987654321",Another Book,Another Author,24.95,5,Hardcover,Another sample description for inventory upload.
"9781234567890",Third Example Book,Third Author,29.99,15,Paperback,Example of a properly formatted CSV entry.'''
    
    # Create response with CSV content
    response = make_response(csv_content)
    response.headers["Content-Disposition"] = "attachment; filename=sample_inventory.csv"
    response.headers["Content-Type"] = "text/csv"
    return response

# Debug route to show all ISBNs in database
@app.route('/debug/isbns')
@login_required
@manager_required
def debug_isbns():
    books = Book.query.order_by(Book.isbn).all()
    isbn_list = [f"<li>{book.isbn} - {book.title} by {book.author}</li>" for book in books]
    return f"<h3>All ISBNs in Database ({len(books)} books):</h3><ul>{''.join(isbn_list)}</ul>"

# Upload CSV
@app.route('/upload_csv', methods=['POST'])
@login_required
@manager_required
def upload_csv():
    file = request.files.get('file')
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        file.save(filepath)

        try:
            with open(filepath, newline='', encoding='utf-8') as csvfile:
                # Read and process headers
                reader = csv.DictReader(csvfile)
                
                # Handle BOM in first column name if present
                fieldnames = reader.fieldnames
                if fieldnames and fieldnames[0].startswith('\ufeff'):
                    fieldnames[0] = fieldnames[0].lstrip('\ufeff')
                
                # Normalize header names to lowercase
                normalized_fieldnames = [h.strip().lower() for h in fieldnames]
                
                # Reset file pointer and create new DictReader with normalized headers
                csvfile.seek(0)
                next(csvfile)  # Skip header line
                reader = csv.DictReader(csvfile, fieldnames=normalized_fieldnames)

                # Counters for feedback
                added_count = 0
                updated_count = 0
                skipped_count = 0

                for row in reader:
                    # Clean and process ISBN - handle scientific notation
                    isbn_raw = row.get('isbn', '').strip()
                    if isbn_raw:
                        try:
                            # Convert scientific notation to regular number if needed
                            if 'E' in isbn_raw.upper():
                                isbn = str(int(float(isbn_raw)))
                            else:
                                isbn = isbn_raw
                        except (ValueError, OverflowError):
                            isbn = isbn_raw  # Use as-is if conversion fails
                    else:
                        isbn = ''
                    
                    title = row.get('title', '').strip()
                    author = row.get('author', '').strip()

                    # Better handling of price and quantity with detailed error messages
                    try:
                        price_raw = row.get('price', '0').strip()
                        if not price_raw or price_raw == '':
                            price = 0.0
                        else:
                            price = float(price_raw.replace('$', '').replace(',', ''))
                    except (ValueError, AttributeError) as e:
                        flash(f"Skipping row - invalid price '{row.get('price')}' for book '{title}': {str(e)}", 'warning')
                        skipped_count += 1
                        continue

                    try:
                        quantity_raw = row.get('quantity', '0').strip()
                        if not quantity_raw or quantity_raw == '':
                            quantity = 0
                        else:
                            quantity = int(float(quantity_raw))  # Handle decimal quantities
                    except (ValueError, AttributeError) as e:
                        flash(f"Skipping row - invalid quantity '{row.get('quantity')}' for book '{title}': {str(e)}", 'warning')
                        skipped_count += 1
                        continue

                    # Validate required fields with better error messages
                    missing_fields = []
                    if not isbn:
                        missing_fields.append('ISBN')
                    if not title:
                        missing_fields.append('title')
                    if not author:
                        missing_fields.append('author')
                    
                    if missing_fields:
                        flash(f"Skipping row - missing required fields: {', '.join(missing_fields)}. Book: '{title or 'Unknown'}'", 'warning')
                        skipped_count += 1
                        continue

                    cover_type = row.get('cover_type', '').strip()
                    description = row.get('description', '').strip()

                    book = Book.query.get(isbn)
                    if book:
                        # Update existing book
                        book.title = title
                        book.author = author
                        book.price = price
                        book.quantity = quantity
                        book.in_stock = quantity > 0
                        book.cover_type = cover_type
                        book.description = description
                        updated_count += 1
                    else:
                        # Add new book
                        book = Book(
                            isbn=isbn,
                            title=title,
                            author=author,
                            price=price,
                            quantity=quantity,
                            in_stock=quantity > 0,
                            cover_type=cover_type,
                            description=description
                        )
                        db.session.add(book)
                        added_count += 1

                db.session.commit()
            
            # Provide detailed feedback about the upload results
            if added_count > 0 or updated_count > 0:
                message_parts = []
                if added_count > 0:
                    message_parts.append(f"{added_count} book(s) added")
                if updated_count > 0:
                    message_parts.append(f"{updated_count} book(s) updated")
                if skipped_count > 0:
                    message_parts.append(f"{skipped_count} row(s) skipped")
                
                success_message = "CSV processed successfully: " + ", ".join(message_parts)
                flash(success_message, 'success')
            else:
                flash("No books were processed from the CSV file.", 'warning')
        except Exception as e:
            flash(f"Error processing CSV: {e}", 'danger')
    else:
        flash("Invalid file type. Please upload a CSV file.", 'danger')

    return redirect(url_for('inventory'))


@app.route('/export_inventory')
@login_required
@manager_required
def export_inventory():
    """Export current inventory to CSV file."""
    try:
        # Get all books from inventory
        books = Book.query.order_by(Book.isbn).all()
        
        # Create CSV content
        output = []
        output.append(['isbn', 'title', 'author', 'price', 'quantity', 'cover_type', 'description', 'in_stock'])
        
        for book in books:
            output.append([
                book.isbn,
                book.title,
                book.author,
                book.price,
                book.quantity,
                book.cover_type or '',
                book.description or '',
                'Yes' if book.in_stock else 'No'
            ])
        
        # Generate CSV response
        def generate():
            for row in output:
                yield ','.join([f'"{str(field)}"' for field in row]) + '\n'
        
        # Create filename with current date
        filename = f"inventory_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        response = make_response(generate())
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = f'attachment; filename={filename}'
        
        flash(f'Inventory exported successfully! {len(books)} books exported.', 'success')
        return response
        
    except Exception as e:
        flash(f"Error exporting inventory: {e}", 'danger')
        return redirect(url_for('inventory'))


# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        print(f"Login attempt: username={username}")
        
        user = User.query.filter_by(username=username).first()
        
        if user:
            print(f"User found: {user.username}")
            print(f"Email: {user.email}")
            print(f"Is Manager: {user.is_manager}")
            print(f"Has password_hash: {bool(user.password_hash)}")
            print(f"Has legacy password: {bool(user.password)}")
            
            if user.check_password(password):
                print("Password check passed")
                
                # Check if user has email for 2FA
                if not user.email:
                    print("No email configured for user")
                    flash('Admin account requires email for security verification. Please contact system administrator.', 'danger')
                    return render_template('login.html')
                
                print(f"Attempting to send 2FA code to {user.email}")
                
                # Send 2FA code
                if send_2fa_code(user):
                    print("2FA code sent successfully")
                    # Store user ID in session for 2FA verification
                    session['pending_2fa_user_id'] = user.id
                    session['2fa_expires'] = (datetime.now() + timedelta(minutes=10)).isoformat()
                    flash('Security code sent to your email. Please check your inbox.', 'info')
                    return redirect(url_for('verify_2fa'))
                else:
                    print("Failed to send 2FA code")
                    flash('Failed to send security code. Please try again.', 'danger')
                    return render_template('login.html')
            else:
                print("Password check failed")
                flash('Invalid username or password.', 'danger')
        else:
            print("User not found")
            flash('Invalid username or password.', 'danger')
        
        # Invalid login - redirect back to login page
    return render_template('login.html')


@app.route('/verify_2fa', methods=['GET', 'POST'])
def verify_2fa():
    # Check if user is in 2FA process
    if 'pending_2fa_user_id' not in session:
        return redirect(url_for('login'))
    
    # Check if 2FA session has expired
    if 'expires' in session and datetime.now() > datetime.fromisoformat(session.get('2fa_expires', '')):
        session.pop('pending_2fa_user_id', None)
        session.pop('2fa_expires', None)
        flash('Security code expired. Please login again.', 'warning')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        code = request.form.get('code', '').strip()
        user_id = session.get('pending_2fa_user_id')
        user = User.query.get(user_id)
        
        if user and user.verify_2fa_code(code):
            # 2FA successful - complete login
            db.session.commit()
            login_user(user, remember=False)  # Don't remember user - session expires when browser closes
            
            # Clear 2FA session data
            session.pop('pending_2fa_user_id', None)
            session.pop('2fa_expires', None)
            
            # Redirect based on user role
            if user.is_manager:
                next_page = request.args.get('next') or url_for('admin_dashboard')
            else:
                next_page = request.args.get('next') or url_for('index')
            return redirect(next_page)
        else:
            flash('Invalid security code. Please try again.', 'danger')
    
    return render_template('verify_2fa.html')


# ================================
# SESSION TIMEOUT ROUTES
# ================================

@app.route('/api/session_status')
@login_required
def session_status():
    """API endpoint to check session status and time remaining."""
    if not current_user.is_manager:
        return jsonify({'error': 'Not authorized'}), 403
    
    last_activity_str = session.get('last_activity')
    if not last_activity_str:
        # No activity tracked yet, start tracking
        session['last_activity'] = datetime.utcnow().isoformat()
        return jsonify({
            'active': True,
            'minutes_remaining': ADMIN_SESSION_TIMEOUT.total_seconds() / 60,
            'warning_threshold': SESSION_WARNING_TIME.total_seconds() / 60
        })
    
    try:
        last_activity = datetime.fromisoformat(last_activity_str)
        time_since_activity = datetime.utcnow() - last_activity
        time_remaining = ADMIN_SESSION_TIMEOUT - time_since_activity
        
        if time_remaining.total_seconds() <= 0:
            return jsonify({
                'active': False,
                'expired': True,
                'message': 'Session has expired'
            })
        
        return jsonify({
            'active': True,
            'minutes_remaining': time_remaining.total_seconds() / 60,
            'warning_threshold': SESSION_WARNING_TIME.total_seconds() / 60,
            'show_warning': time_remaining <= (ADMIN_SESSION_TIMEOUT - SESSION_WARNING_TIME)
        })
    
    except (ValueError, TypeError):
        # Invalid timestamp, reset
        session['last_activity'] = datetime.utcnow().isoformat()
        return jsonify({
            'active': True,
            'minutes_remaining': ADMIN_SESSION_TIMEOUT.total_seconds() / 60,
            'warning_threshold': SESSION_WARNING_TIME.total_seconds() / 60
        })


@app.route('/api/extend_session', methods=['POST'])
@login_required
def extend_session():
    """API endpoint to extend the current session."""
    if not current_user.is_manager:
        return jsonify({'error': 'Not authorized'}), 403
    
    # Reset last activity to current time
    session['last_activity'] = datetime.utcnow().isoformat()
    
    return jsonify({
        'success': True,
        'message': 'Session extended successfully',
        'minutes_remaining': ADMIN_SESSION_TIMEOUT.total_seconds() / 60
    })


@app.route('/api/check_timeout')
@login_required  
def check_timeout():
    """API endpoint to check if session should be terminated."""
    if not current_user.is_manager:
        return jsonify({'error': 'Not authorized'}), 403
        
    if check_session_timeout():
        logout_user()
        session.pop('last_activity', None)
        return jsonify({
            'expired': True,
            'message': 'Session expired due to inactivity'
        })
    
    return jsonify({'expired': False})


@app.route('/logout')
@login_required
def logout():
    # Clear any pending 2FA session data
    session.pop('pending_2fa_user_id', None)
    session.pop('2fa_expires', None)
    session.pop('last_activity', None)  # Clear session timeout tracking
    
    # Clear 2FA verification status for the user
    if current_user.is_authenticated:
        current_user.two_fa_verified = False
        current_user.clear_2fa_code()
        try:
            db.session.commit()
        except:
            db.session.rollback()
    
    logout_user()
    return redirect(url_for('login'))


@app.route('/logout_ajax', methods=['POST'])
def logout_ajax():
    """AJAX endpoint for automatic logout when browser closes"""
    try:
        # Clear any pending 2FA session data
        session.pop('pending_2fa_user_id', None)
        session.pop('2fa_expires', None)
        
        # Clear 2FA verification status for the user
        if current_user.is_authenticated:
            current_user.two_fa_verified = False
            current_user.clear_2fa_code()
            try:
                db.session.commit()
            except:
                db.session.rollback()
        
        logout_user()
        return jsonify({'status': 'success', 'message': 'Logged out successfully'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})


# Admin Forgot Password Routes
@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Admin forgot password - request reset token."""
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        
        if not email:
            flash('Please enter your email address.', 'danger')
            return render_template('forgot_password.html')
        
        # Find user by email
        user = User.query.filter_by(email=email).first()
        
        if user:
            # Generate reset token
            reset_token = user.generate_reset_token()
            db.session.commit()
            
            # Send reset email
            email_sent = send_password_reset_email(user.email, reset_token, is_customer=False)
            
            if email_sent:
                flash('Password reset instructions have been sent to your email address.', 'info')
            else:
                flash('There was an issue sending the reset email. Please try again later.', 'danger')
        else:
            # For security, don't reveal if email exists or not
            flash('If the email address exists in our system, you will receive reset instructions.', 'info')
        
        return redirect(url_for('login'))
    
    return render_template('forgot_password.html')


@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Admin reset password with token."""
    # Find user with valid token
    user = User.query.filter_by(reset_token=token).first()
    
    if not user or not user.verify_reset_token(token):
        flash('Invalid or expired reset token.', 'danger')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        new_password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        if not new_password or not confirm_password:
            flash('Please enter both password fields.', 'danger')
            return render_template('reset_password.html', token=token)
        
        if new_password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('reset_password.html', token=token)
        
        if len(new_password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
            return render_template('reset_password.html', token=token)
        
        # Update password and clear reset token
        user.set_password(new_password)
        user.clear_reset_token()
        db.session.commit()
        
        flash('Your password has been reset successfully. You can now log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('reset_password.html', token=token)


# Customer Forgot Password Routes
@app.route('/customer/forgot-password', methods=['GET', 'POST'])
def customer_forgot_password():
    """Customer forgot password - request reset token."""
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        
        if not email:
            flash('Please enter your email address.', 'danger')
            return render_template('customer_forgot_password.html')
        
        # Find customer by email
        customer = Customer.query.filter_by(email=email).first()
        
        if customer:
            # Generate reset token
            reset_token = customer.generate_reset_token()
            db.session.commit()
            
            # Send reset email
            email_sent = send_password_reset_email(customer.email, reset_token, is_customer=True)
            
            if email_sent:
                flash('Password reset instructions have been sent to your email address.', 'info')
            else:
                flash('There was an issue sending the reset email. Please try again later.', 'danger')
        else:
            # For security, don't reveal if email exists or not
            flash('If the email address exists in our system, you will receive reset instructions.', 'info')
        
        return redirect(url_for('customer_login'))
    
    return render_template('customer_forgot_password.html')


@app.route('/customer/reset-password/<token>', methods=['GET', 'POST'])
def customer_reset_password(token):
    """Customer reset password with token."""
    # Find customer with valid token
    customer = Customer.query.filter_by(reset_token=token).first()
    
    if not customer or not customer.verify_reset_token(token):
        flash('Invalid or expired reset token.', 'danger')
        return redirect(url_for('customer_login'))
    
    if request.method == 'POST':
        new_password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        if not new_password or not confirm_password:
            flash('Please enter both password fields.', 'danger')
            return render_template('customer_reset_password.html', token=token)
        
        if new_password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('customer_reset_password.html', token=token)
        
        if len(new_password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
            return render_template('customer_reset_password.html', token=token)
        
        # Update password and clear reset token
        customer.set_password(new_password)
        customer.clear_reset_token()
        db.session.commit()
        
        flash('Your password has been reset successfully. You can now log in.', 'success')
        return redirect(url_for('customer_login'))
    
    return render_template('customer_reset_password.html', token=token)


@app.route('/all_orders')
@login_required
@manager_required
def all_orders():
    """Show both legacy orders and new purchases in a unified view."""
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    status = request.args.get('status')

    # Get orders from Purchase table (since Order table is empty)
    purchases_query = Purchase.query
    
    # Apply filters if provided
    if start_date:
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        purchases_query = purchases_query.filter(Purchase.timestamp >= start_dt)
    if end_date:
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        purchases_query = purchases_query.filter(Purchase.timestamp <= end_dt)
    if status:
        purchases_query = purchases_query.filter(Purchase.status == status)

    # Get all matching purchases and convert to a format the template expects
    all_purchases = purchases_query.order_by(Purchase.timestamp.desc()).all()
    
    # Convert purchases to the format expected by the template
    all_items = []
    for p in all_purchases:
        # Create an object with the attributes the template expects
        item = type('obj', (object,), {
            'id': p.id,
            'source': 'purchase',
            'customer_name': p.customer_name,
            'customer_email': p.customer_email,
            'customer_phone': p.customer_phone,
            'customer_address': p.customer_address,
            'book_isbn': p.book_isbn,
            'quantity': p.quantity,
            'status': p.status,
            'timestamp': p.timestamp,
            'timestamp_str': p.timestamp.strftime('%Y-%m-%d %H:%M') if p.timestamp else ''
        })()
        all_items.append(item)

    # Get unique statuses for the filter dropdown
    unique_statuses = set()
    for item in all_items:
        if item.status:
            unique_statuses.add(item.status)
    unique_statuses = sorted(list(unique_statuses))

    return render_template('all_orders.html', 
                         orders=all_items,
                         current_status=status,
                         current_start_date=start_date,
                         current_end_date=end_date,
                         statuses=unique_statuses)


@app.route('/api/update_order/<source>/<int:order_id>', methods=['POST'])
@login_required
@manager_required
def api_update_order(source, order_id):
    """API endpoint to update order/purchase status from the combined view."""
    try:
        print(f"API update called: source={source}, order_id={order_id}")
        
        # Ensure we return JSON even for auth failures
        if not current_user.is_authenticated:
            return jsonify({'error': 'Authentication required', 'redirect': url_for('login')}), 401
        
        if not getattr(current_user, 'is_manager', False):
            return jsonify({'error': 'Manager access required'}), 403
        
        if source == 'legacy':
            item = Order.query.get(order_id)
        else:
            item = Purchase.query.get(order_id)
        
        print(f"Item found: {item}")
        if not item:
            print("Item not found!")
            return jsonify({'error': 'Order not found'}), 404
        
        status = request.form.get('status')
        print(f"Status to set: {status}")
        
        if not status:
            print("No status provided!")
            return jsonify({'error': 'Status not provided'}), 400
        
        old_status = item.status
        item.status = status
        db.session.commit()
        
        # Send admin notification for status change
        if hasattr(item, 'customer_name'):  # It's a Purchase object
            try:
                send_admin_notification(
                    subject=f"Order Status Changed - Chapter 6: A Plot Twist",
                    message=f"Order status has been changed by {current_user.username}.\n\nStatus changed from '{old_status}' to '{status}' for order #{item.id}.",
                    order_details=get_order_details_dict(item)
                )
            except Exception as e:
                print(f"Failed to send admin notification: {e}")
        
        print(f"Status updated successfully.")
        return jsonify({
            'status': 'success', 
            'message': f'{source.title()} order {order_id} updated to {status}',
            'old_status': old_status,
            'new_status': status
        }), 200
        
    except Exception as e:
        print(f"Exception in api_update_order: {e}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500


# ================================
# CUSTOMER AUTHENTICATION ROUTES
# ================================

@app.route('/customer/register', methods=['GET', 'POST'])
def customer_register():
    """Customer registration page with notification preferences."""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Handle both forms: register.html (first_name + last_name) and customer_register.html (full_name)
        full_name = request.form.get('full_name', '').strip()
        if not full_name:
            first_name = request.form.get('first_name', '').strip()
            last_name = request.form.get('last_name', '').strip()
            full_name = f"{first_name} {last_name}".strip()
        
        phone = request.form.get('phone', '').strip()
        
        # Separate address fields
        address_line1 = request.form.get('addressLine1', '').strip()
        address_line2 = request.form.get('addressLine2', '').strip()
        city = request.form.get('city', '').strip()
        state = request.form.get('state', '').strip()
        zip_code = request.form.get('zip', '').strip()
        
        # Combine address fields into single address string for storage
        address_parts = [address_line1]
        if address_line2:
            address_parts.append(address_line2)
        if city:
            address_parts.append(city)
        if state:
            address_parts.append(state)
        if zip_code:
            address_parts.append(zip_code)
        address = ', '.join(address_parts) if address_parts else None
        
        receive_marketing = 'receive_marketing' in request.form
        
        # Notification preferences
        book_interests = request.form.get('book_interests', '').strip()
        genre_interests = request.form.getlist('genres')
        
        # Validation
        errors = []
        
        if not username or len(username) < 3:
            errors.append('Username must be at least 3 characters long.')
        
        if not email or '@' not in email:
            errors.append('Please enter a valid email address.')
        
        if not password or len(password) < 6:
            errors.append('Password must be at least 6 characters long.')
        
        if password != confirm_password:
            errors.append('Passwords do not match.')
        
        if not full_name:
            errors.append('Full name is required.')
        
        # Check if username or email already exists
        if Customer.query.filter_by(username=username).first():
            errors.append('Username already exists. Please choose a different one.')
        
        if Customer.query.filter_by(email=email).first():
            errors.append('Email already registered. Please use a different email or login.')
        
        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('customer_register.html')
        
        # Create new customer
        try:
            new_customer = Customer(
                username=username,
                email=email,
                full_name=full_name,
                phone=phone if phone else None,
                address=address if address else None,
                address_line1=address_line1 if address_line1 else None,
                address_line2=address_line2 if address_line2 else None,
                city=city if city else None,
                state=state if state else None,
                zip_code=zip_code if zip_code else None,
                receive_marketing=receive_marketing
            )
            new_customer.set_password(password)
            
            db.session.add(new_customer)
            db.session.commit()
            
            # Add book notification preferences
            if book_interests:
                book_titles = [title.strip() for title in book_interests.split('\n') if title.strip()]
                for book_title in book_titles:
                    book_notification = BookNotification(
                        customer_id=new_customer.id,
                        book_title=book_title
                    )
                    db.session.add(book_notification)
            
            # Add genre notification preferences
            for genre in genre_interests:
                genre_notification = GenreNotification(
                    customer_id=new_customer.id,
                    genre=genre
                )
                db.session.add(genre_notification)
            
            db.session.commit()
            
            flash('Registration successful! You can now login. We\'ll notify you about your book and genre interests.', 'success')
            return redirect(url_for('customer_login'))
        
        except Exception as e:
            db.session.rollback()
            flash('Registration failed. Please try again.', 'danger')
            print(f"Registration error: {e}")
    
    return render_template('customer_register.html')


@app.route('/customer/login', methods=['GET', 'POST'])
def customer_login():
    """Customer login page."""
    if request.method == 'POST':
        username_or_email = request.form.get('username_or_email', '').strip()
        password = request.form.get('password', '')
        remember_me = 'remember_me' in request.form
        
        if not username_or_email or not password:
            flash('Please enter both username/email and password.', 'danger')
            return render_template('customer_login.html')
        
        # Try to find customer by username or email
        customer = Customer.query.filter(
            (Customer.username == username_or_email) | 
            (Customer.email == username_or_email)
        ).first()
        
        if customer and customer.check_password(password) and customer.is_active:
            login_user(customer, remember=remember_me)
            flash(f'Welcome back, {customer.full_name}!', 'success')
            
            # Redirect to intended page or customer dashboard
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('customer_dashboard'))
        else:
            flash('Invalid username/email or password.', 'danger')
    
    return render_template('customer_login.html')


@app.route('/customer/logout')
def customer_logout():
    """Customer logout."""
    if current_user.is_authenticated and hasattr(current_user, 'username'):
        logout_user()
        flash('You have been logged out successfully.', 'info')
    return redirect(url_for('browse'))


@app.route('/customer/dashboard')
def customer_dashboard():
    """Customer dashboard - main landing page after login."""
    if not current_user.is_authenticated or not hasattr(current_user, 'email'):
        flash('Please login to access your account.', 'warning')
        return redirect(url_for('customer_login'))
    
    return render_template('customer_dashboard.html', customer=current_user)


@app.route('/customer/account')
def customer_account():
    """Customer account management page."""
    if not current_user.is_authenticated or not hasattr(current_user, 'email'):
        flash('Please login to access your account.', 'warning')
        return redirect(url_for('customer_login'))
    
    return render_template('customer_account.html', customer=current_user)


@app.route('/customer/account/edit', methods=['GET', 'POST'])
def edit_customer_account():
    """Edit customer account information."""
    if not current_user.is_authenticated or not hasattr(current_user, 'email'):
        flash('Please login to access your account.', 'warning')
        return redirect(url_for('customer_login'))
    
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        
        # Separate address fields
        address_line1 = request.form.get('address_line1', '').strip()
        address_line2 = request.form.get('address_line2', '').strip()
        city = request.form.get('city', '').strip()
        state = request.form.get('state', '').strip()
        zip_code = request.form.get('zip_code', '').strip()
        
        # Combine address fields for backward compatibility
        address_parts = [address_line1]
        if address_line2:
            address_parts.append(address_line2)
        if city:
            address_parts.append(city)
        if state:
            address_parts.append(state)
        if zip_code:
            address_parts.append(zip_code)
        address = ', '.join(address_parts) if address_parts else None
        
        receive_marketing = 'receive_marketing' in request.form
        
        # Validation
        errors = []
        
        if not full_name:
            errors.append('Full name is required.')
        
        if not email or '@' not in email:
            errors.append('Please enter a valid email address.')
        
        # Check if email is taken by another customer
        existing_customer = Customer.query.filter(
            Customer.email == email,
            Customer.id != current_user.id
        ).first()
        
        if existing_customer:
            errors.append('Email is already in use by another account.')
        
        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('edit_customer_account.html', customer=current_user)
        
        # Update customer information
        try:
            current_user.full_name = full_name
            current_user.email = email
            current_user.phone = phone if phone else None
            current_user.address = address if address else None
            current_user.address_line1 = address_line1 if address_line1 else None
            current_user.address_line2 = address_line2 if address_line2 else None
            current_user.city = city if city else None
            current_user.state = state if state else None
            current_user.zip_code = zip_code if zip_code else None
            current_user.receive_marketing = receive_marketing
            
            db.session.commit()
            flash('Account information updated successfully!', 'success')
            return redirect(url_for('customer_account'))
        
        except Exception as e:
            db.session.rollback()
            flash('Error updating account information. Please try again.', 'danger')
            print(f"Account update error: {e}")
    
    return render_template('edit_customer_account.html', customer=current_user, now=datetime.now)


@app.route('/customer/orders')
def customer_orders():
    """Customer order history."""
    if not current_user.is_authenticated or not hasattr(current_user, 'email'):
        flash('Please login to view your orders.', 'warning')
        return redirect(url_for('customer_login'))
    
    # Get customer's purchase history
    purchases = Purchase.query.filter_by(customer_email=current_user.email).order_by(Purchase.timestamp.desc()).all()
    
    # Group purchases by date for better display
    purchase_groups = {}
    for purchase in purchases:
        date_key = purchase.timestamp.date()
        if date_key not in purchase_groups:
            purchase_groups[date_key] = []
        
        # Get book information
        book = Book.query.filter_by(isbn=purchase.book_isbn).first()
        purchase_groups[date_key].append({
            'purchase': purchase,
            'book': book
        })
    
    return render_template('customer_orders.html', 
                         purchase_groups=purchase_groups,
                         customer=current_user)


@app.route('/customer/orders/<int:purchase_id>')
def customer_order_detail(purchase_id):
    """View details of a specific customer order."""
    if not current_user.is_authenticated or not hasattr(current_user, 'email'):
        flash('Please login to view order details.', 'warning')
        return redirect(url_for('customer_login'))
    
    # Get the purchase and verify it belongs to the current customer
    purchase = Purchase.query.filter_by(
        id=purchase_id, 
        customer_email=current_user.email
    ).first()
    
    if not purchase:
        flash('Order not found or access denied.', 'danger')
        return redirect(url_for('customer_orders'))
    
    # Get book information
    book = Book.query.filter_by(isbn=purchase.book_isbn).first()
    
    return render_template('customer_order_detail.html', 
                         purchase=purchase,
                         book=book,
                         customer=current_user)


@app.route('/customer/notifications', methods=['GET', 'POST'])
def customer_notifications():
    """Customer notification management page."""
    if not current_user.is_authenticated or not hasattr(current_user, 'email'):
        flash('Please login to manage your notifications.', 'warning')
        return redirect(url_for('customer_login'))
    
    if request.method == 'POST':
        new_book_title = request.form.get('new_book_title', '').strip()
        new_genre = request.form.get('new_genre', '').strip()
        
        success_messages = []
        
        # Add book notification
        if new_book_title:
            # Check if already exists
            existing = BookNotification.query.filter_by(
                customer_id=current_user.id,
                book_title=new_book_title
            ).first()
            
            if not existing:
                book_notification = BookNotification(
                    customer_id=current_user.id,
                    book_title=new_book_title
                )
                db.session.add(book_notification)
                success_messages.append(f'Added book notification for "{new_book_title}"')
            else:
                flash(f'You already have a notification set up for "{new_book_title}".', 'warning')
        
        # Add genre notification
        if new_genre:
            # Check if already exists
            existing = GenreNotification.query.filter_by(
                customer_id=current_user.id,
                genre=new_genre
            ).first()
            
            if not existing:
                genre_notification = GenreNotification(
                    customer_id=current_user.id,
                    genre=new_genre
                )
                db.session.add(genre_notification)
                success_messages.append(f'Added genre notification for "{new_genre}"')
            else:
                flash(f'You already have a notification set up for "{new_genre}" genre.', 'warning')
        
        # Commit changes
        if success_messages:
            try:
                db.session.commit()
                for message in success_messages:
                    flash(message, 'success')
            except Exception as e:
                db.session.rollback()
                flash('Error adding notifications. Please try again.', 'danger')
                print(f"Notification add error: {e}")
        
        return redirect(url_for('customer_notifications'))
    
    # Get customer's current notifications
    book_notifications = BookNotification.query.filter_by(
        customer_id=current_user.id
    ).order_by(BookNotification.created_date.desc()).all()
    
    genre_notifications = GenreNotification.query.filter_by(
        customer_id=current_user.id
    ).order_by(GenreNotification.created_date.desc()).all()
    
    # Get notification history
    notification_logs = NotificationLog.query.filter_by(
        customer_id=current_user.id
    ).order_by(NotificationLog.sent_date.desc()).limit(20).all()
    
    return render_template('customer_notifications.html',
                         customer=current_user,
                         book_notifications=book_notifications,
                         genre_notifications=genre_notifications,
                         notification_logs=notification_logs)


@app.route('/customer/notifications/remove', methods=['POST'])
def remove_notification():
    """Remove a book or genre notification."""
    if not current_user.is_authenticated or not hasattr(current_user, 'email'):
        flash('Please login to manage your notifications.', 'warning')
        return redirect(url_for('customer_login'))
    
    notification_type = request.form.get('notification_type')
    notification_id = request.form.get('notification_id')
    
    if not notification_type or not notification_id:
        flash('Invalid notification removal request.', 'danger')
        return redirect(url_for('customer_notifications'))
    
    try:
        if notification_type == 'book':
            notification = BookNotification.query.filter_by(
                id=notification_id,
                customer_id=current_user.id
            ).first()
            
            if notification:
                db.session.delete(notification)
                db.session.commit()
                flash(f'Removed book notification for "{notification.book_title}".', 'info')
            else:
                flash('Notification not found.', 'danger')
                
        elif notification_type == 'genre':
            notification = GenreNotification.query.filter_by(
                id=notification_id,
                customer_id=current_user.id
            ).first()
            
            if notification:
                db.session.delete(notification)
                db.session.commit()
                flash(f'Removed genre notification for "{notification.genre}".', 'info')
            else:
                flash('Notification not found.', 'danger')
        
        else:
            flash('Invalid notification type.', 'danger')
    
    except Exception as e:
        db.session.rollback()
        flash('Error removing notification. Please try again.', 'danger')
        print(f"Notification removal error: {e}")
    
    return redirect(url_for('customer_notifications'))


# Browse route for customer-facing book browsing
@app.route('/browse')
def browse():
    """Browse books with search functionality for customers."""
    search_query = request.args.get('q', '').strip()
    
    if search_query:
        books = Book.query.filter(
            or_(
                Book.title.ilike(f'%{search_query}%'),
                Book.author.ilike(f'%{search_query}%'),
                Book.isbn.ilike(f'%{search_query}%')
            )
        ).all()
    else:
        books = Book.query.all()
    
    return render_template('index.html', inventory=books, search_query=search_query)


# =============================================================================
# CUSTOMER SHOPPING CART ROUTES
# =============================================================================
# =============================================================================
# CUSTOMER SHOPPING CART ROUTES
# =============================================================================

# Admin User Management Routes
@app.route('/admin/users')
@login_required
@manager_required
def admin_users():
    """Display all admin users with notification preferences."""
    users = User.query.filter_by(is_manager=True).all()
    return render_template('admin_users.html', users=users)


@app.route('/admin/users/create', methods=['GET', 'POST'])
@login_required
@manager_required
def create_admin_user():
    """Create a new admin user."""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        full_name = request.form.get('full_name')
        receive_notifications = 'receive_notifications' in request.form
        
        # Validation
        if not username or not password or not email:
            flash('Username, password, and email are required.', 'danger')
            return render_template('create_admin_user.html')
        
        # Check if user already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists.', 'danger')
            return render_template('create_admin_user.html')
        
        # Check if email already exists
        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            flash('Email already exists.', 'danger')
            return render_template('create_admin_user.html')
        
        # Create new admin user
        hashed_password = generate_password_hash(password)
        new_user = User(
            username=username,
            password=hashed_password,
            is_manager=True,
            email=email,
            full_name=full_name or username,
            receive_notifications=receive_notifications
        )
        
        try:
            db.session.add(new_user)
            db.session.commit()
            flash(f'Admin user "{username}" created successfully.', 'success')
            return redirect(url_for('admin_users'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating user: {e}', 'danger')
    
    return render_template('create_admin_user.html')


@app.route('/admin/users/create_dashboard', methods=['POST'])
@login_required
@manager_required
def create_admin_user_dashboard():
    """Create a new admin user from the dashboard modal."""
    username = request.form.get('username')
    password = request.form.get('password')
    email = request.form.get('email')
    full_name = request.form.get('full_name')
    receive_notifications = 'receive_notifications' in request.form
    
    # Validation
    if not username or not password or not email:
        flash('Username, password, and email are required.', 'danger')
        return redirect(url_for('admin_dashboard'))
    
    # Check if user already exists
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        flash(f'Username "{username}" already exists.', 'danger')
        return redirect(url_for('admin_dashboard'))
    
    # Check if email already exists
    existing_email = User.query.filter_by(email=email).first()
    if existing_email:
        flash(f'Email "{email}" is already in use.', 'danger')
        return redirect(url_for('admin_dashboard'))
    
    # Create new admin user
    hashed_password = generate_password_hash(password)
    new_user = User(
        username=username,
        password=hashed_password,
        is_manager=True,
        email=email,
        full_name=full_name or username,
        receive_notifications=receive_notifications
    )
    
    try:
        db.session.add(new_user)
        db.session.commit()
        
        notification_status = "with notifications enabled" if receive_notifications else "with notifications disabled"
        flash(f'Admin user "{username}" created successfully {notification_status}!', 'success')
        
        # Log the creation
        print(f"New admin user created: {username} ({email}) by {current_user.username}")
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error creating admin user: {e}', 'danger')
    
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/users/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
@manager_required
def edit_admin_user(user_id):
    """Edit an existing admin user."""
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        email = request.form.get('email')
        full_name = request.form.get('full_name')
        receive_notifications = 'receive_notifications' in request.form
        new_password = request.form.get('password')
        
        # Validation
        if not email:
            flash('Email is required.', 'danger')
            return render_template('edit_admin_user.html', user=user)
        
        # Check if email already exists (but not for this user)
        existing_email = User.query.filter(User.email == email, User.id != user_id).first()
        if existing_email:
            flash('Email already exists.', 'danger')
            return render_template('edit_admin_user.html', user=user)
        
        # Update user
        user.email = email
        user.full_name = full_name or user.username
        user.receive_notifications = receive_notifications
        
        if new_password:
            user.password = generate_password_hash(new_password)
        
        try:
            db.session.commit()
            flash(f'Admin user "{user.username}" updated successfully.', 'success')
            return redirect(url_for('admin_users'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating user: {e}', 'danger')
    
    return render_template('edit_admin_user.html', user=user)


@app.route('/admin/users/delete/<int:user_id>', methods=['POST'])
@login_required
@manager_required
def delete_admin_user(user_id):
    """Delete an admin user."""
    user = User.query.get_or_404(user_id)
    
    # Prevent deletion of current user
    if user.id == current_user.id:
        flash('You cannot delete your own account.', 'danger')
        return redirect(url_for('admin_users'))
    
    try:
        db.session.delete(user)
        db.session.commit()
        flash(f'Admin user "{user.username}" deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting user: {e}', 'danger')
    
    return redirect(url_for('admin_users'))


# =============================================================================
# CUSTOMER SHOPPING CART ROUTES
# =============================================================================

@app.route('/add_to_cart/<isbn>', methods=['POST'])
def add_to_cart(isbn):
    """Add a book to the shopping cart."""
    quantity = int(request.form.get('quantity', 1))
    book = Book.query.filter_by(isbn=isbn).first()
    
    if not book:
        flash("Book not found.", 'danger')
        return redirect(url_for('browse'))
    
    if book.quantity < quantity:
        flash(f"Only {book.quantity} copies available.", 'warning')
        return redirect(url_for('browse'))
    
    # Initialize cart if it doesn't exist
    cart = session.get('cart')
    if not isinstance(cart, dict):
        cart = {}
    
    # Add to cart
    cart[isbn] = cart.get(isbn, 0) + quantity
    session['cart'] = cart
    session.permanent = True
    
    flash(f"{book.title} added to cart (x{quantity}).", 'info')
    return redirect(url_for('browse'))


@app.route('/cart')
def view_cart():
    """Display the shopping cart with discount calculations."""
    cart = session.get('cart', {})
    cart_items = []
    subtotal = 0
    
    for isbn, qty in cart.items():
        book = Book.query.filter_by(isbn=isbn).first()
        if book:
            cart_items.append((book, qty))
            subtotal += book.price * qty
    
    # Calculate discount
    discount_code = session.get('discount_code')
    discount_rate = 0
    discount_amount = 0
    
    if discount_code and discount_code in DISCOUNT_CODES:
        discount_rate, min_order = DISCOUNT_CODES[discount_code]
        if subtotal >= min_order:
            discount_amount = subtotal * discount_rate
    
    total = subtotal - discount_amount
    
    return render_template('cart.html', 
                         cart_items=cart_items, 
                         subtotal=subtotal,
                         total=total,
                         discount_code=discount_code,
                         discount_amount=discount_amount)


@app.route('/update_cart/<isbn>', methods=['POST'])
def update_cart(isbn):
    """Update quantity of an item in the cart."""
    new_qty = int(request.form.get('quantity', 1))
    cart = session.get('cart', {})
    
    if isbn in cart:
        if new_qty > 0:
            cart[isbn] = new_qty
            flash(f"Quantity updated for {isbn}.", 'info')
        else:
            del cart[isbn]
            flash(f"{isbn} removed from cart.", 'warning')
        session['cart'] = cart
        session.permanent = True
    
    return redirect(url_for('view_cart'))


@app.route('/remove_from_cart/<isbn>', methods=['POST'])
def remove_from_cart(isbn):
    """Remove an item from the cart."""
    cart = session.get('cart', {})
    if isbn in cart:
        del cart[isbn]
        session['cart'] = cart
        session.permanent = True
        flash("Item removed from cart.", 'info')
    
    return redirect(url_for('view_cart'))


@app.route('/reset_cart')
def reset_cart():
    """Clear the entire cart."""
    session['cart'] = {}
    session.permanent = True
    flash("Cart reset.", 'info')
    return redirect(url_for('view_cart'))


@app.route('/checkout', methods=['GET'])
def checkout_page():
    """Display checkout page with payment method selection."""
    cart = session.get('cart', {})
    if not cart:
        flash("Cart is empty!", "warning")
        return redirect(url_for('view_cart'))
    
    # Check if user is logged in
    if not current_user.is_authenticated or not hasattr(current_user, 'email'):
        flash('Please login to complete checkout.', 'warning')
        return redirect(url_for('customer_login'))
    
    # Calculate cart totals
    cart_items = []
    subtotal = 0
    
    for isbn, qty in cart.items():
        book = Book.query.filter_by(isbn=isbn).first()
        if book:
            # Check inventory
            if book.quantity < qty:
                flash(f"Not enough inventory for {book.title}. Only {book.quantity} available.", "danger")
                return redirect(url_for('view_cart'))
            cart_items.append((book, qty))
            subtotal += book.price * qty
    
    # Calculate discount
    discount_code = session.get('discount_code')
    discount_amount = 0
    if discount_code and discount_code in DISCOUNT_CODES:
        discount_rate, min_order = DISCOUNT_CODES[discount_code]
        if subtotal >= min_order:
            discount_amount = subtotal * discount_rate
    
    total = subtotal - discount_amount
    
    return render_template('payment.html', 
                         cart_items=cart_items,
                         subtotal=subtotal,
                         discount_amount=discount_amount,
                         total=total,
                         customer=current_user)


@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    """Display payment form for checkout."""
    cart = session.get('cart', {})
    if not cart:
        flash("Cart is empty!", "warning")
        return redirect(url_for('view_cart'))

    # Check if user is logged in
    if not current_user.is_authenticated or not hasattr(current_user, 'email'):
        flash('Please login to complete checkout.', 'warning')
        return redirect(url_for('customer_login'))

    # Calculate cart totals
    subtotal = 0
    cart_items = []
    
    for isbn, qty in cart.items():
        book = Book.query.filter_by(isbn=isbn).first()
        if book:
            # Check if enough inventory
            if book.quantity < qty:
                flash(f"Not enough inventory for {book.title}. Only {book.quantity} available.", "danger")
                return redirect(url_for('view_cart'))
            subtotal += book.price * qty
            cart_items.append((book, qty))

    # Apply discount if applicable
    discount_code = session.get('discount_code')
    discount_amount = 0
    if discount_code and discount_code in DISCOUNT_CODES:
        discount_rate, min_order = DISCOUNT_CODES[discount_code]
        if subtotal >= min_order:
            discount_amount = subtotal * discount_rate

    total = subtotal - discount_amount

    return render_template('payment.html', 
                         cart_items=cart_items,
                         subtotal=subtotal,
                         discount_amount=discount_amount,
                         total=total)


@app.route('/process_checkout', methods=['POST'])
def process_checkout():
    """Complete the purchase and create sales records with payment validation."""
    print("=== PROCESS_CHECKOUT DEBUG ===")
    print(f"Form data: {dict(request.form)}")
    print(f"Cart: {session.get('cart', {})}")
    print(f"User authenticated: {current_user.is_authenticated}")
    
    cart = session.get('cart', {})
    if not cart:
        flash("Cart is empty!", "warning")
        return redirect(url_for('view_cart'))

    # Check if user is logged in
    if not current_user.is_authenticated or not hasattr(current_user, 'email'):
        flash('Please login to complete checkout.', 'warning')
        return redirect(url_for('customer_login'))

    # Get payment method information from form
    payment_method = request.form.get('payment_method')
    print(f"Payment method: {payment_method}")
    
    # Validate payment method and collect details
    payment_details = {}
    try:
        if payment_method == 'credit_card':
            payment_details = {
                'number': request.form.get('card_number', '').replace(' ', ''),
                'expiry': request.form.get('expiry', ''),
                'cvv': request.form.get('cvv', ''),
                'name': request.form.get('cardholder_name', '')
            }
            print(f"Credit card details: {payment_details}")
        elif payment_method == 'paypal':
            payment_details = {
                'email': request.form.get('paypal_email', '')
            }
        elif payment_method == 'bank_transfer':
            payment_details = {
                'routing_number': request.form.get('routing_number', ''),
                'account_number': request.form.get('account_number', ''),
                'bank_name': request.form.get('bank_name', '')
            }
        else:
            print(f"Invalid payment method: {payment_method}")
            flash("Invalid payment method selected.", "danger")
            return redirect(url_for('checkout'))

        # Validate payment method
        print(f"Validating payment method: {payment_method} with details: {payment_details}")
        is_valid, validation_message = validate_payment_method(payment_method, payment_details)
        print(f"Validation result: {is_valid}, message: {validation_message}")
        if not is_valid:
            flash(f"Payment validation failed: {validation_message}", "danger")
            return redirect(url_for('checkout'))
            
    except Exception as e:
        print(f"Exception in payment validation: {str(e)}")
        flash(f"Payment validation error: {str(e)}", "danger")
        return redirect(url_for('checkout'))

    # Continue with the full checkout process
    try:
        # Calculate subtotal first
        subtotal = 0
        for isbn, qty in cart.items():
            book = Book.query.filter_by(isbn=isbn).first()
            if book:
                # Check if enough inventory
                if book.quantity < qty:
                    flash(f"Not enough inventory for {book.title}. Only {book.quantity} available.", "danger")
                    return redirect(url_for('checkout'))
                subtotal += book.price * qty
        
        # Apply discount if applicable
        discount_code = session.get('discount_code')
        discount_amount = 0
        if discount_code and discount_code in DISCOUNT_CODES:
            discount_rate, min_order = DISCOUNT_CODES[discount_code]
            if subtotal >= min_order:
                discount_amount = subtotal * discount_rate
        
        total = subtotal - discount_amount
        
        # Process payment simulation
        try:
            payment_result = process_payment(total, payment_method, payment_details)
            print(f"Payment simulation result: {payment_result}")
        except PaymentError as e:
            error_type, user_message, suggested_action = handle_payment_error(e)
            flash(f"{user_message} {suggested_action}", error_type)
            return redirect(url_for('checkout'))
        
        # Create payment method record
        payment_record = PaymentMethod(
            method_type=payment_method,
            amount=total,
            status='completed'
        )
        
        # Store payment-specific information (secure way)
        if payment_method == 'credit_card':
            payment_record.card_last_four = payment_details['number'][-4:]
            payment_record.card_type = detect_card_type(payment_details['number'])
            payment_record.cardholder_name = payment_details['name']
        elif payment_method == 'paypal':
            payment_record.paypal_email = payment_details['email']
        elif payment_method == 'bank_transfer':
            payment_record.bank_name = payment_details['bank_name']
            payment_record.account_last_four = payment_details['account_number'][-4:]
        
        # Generate transaction ID
        payment_record.transaction_id = 'TXN' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        
        db.session.add(payment_record)
        
        # Process each item in cart
        for isbn, qty in cart.items():
            book = Book.query.filter_by(isbn=isbn).first()
            if book:
                # Calculate total price for this item (without discount - discount is applied to overall total)
                total_price = book.price * qty
                
                # Create sale record
                sale = Sale(book_id=isbn, quantity=qty, total_price=total_price)
                db.session.add(sale)
                
                # Create purchase record for logged-in customers
                purchase = Purchase(
                    customer_name=current_user.full_name,
                    customer_email=current_user.email,
                    customer_phone=current_user.phone,
                    customer_address=current_user.address_line1 or current_user.address,
                    book_isbn=isbn,
                    quantity=qty,
                    status='Confirmed'  # Set initial status
                )
                db.session.add(purchase)
                
                # Update book inventory
                book.quantity -= qty
                if book.quantity == 0:
                    book.in_stock = False

        # Commit all changes
        db.session.commit()
        
        # Prepare purchase details for customer notification
        purchase_details = []
        for isbn, qty in cart.items():
            book = Book.query.filter_by(isbn=isbn).first()
            if book:
                purchase_details.append({
                    'title': book.title,
                    'quantity': qty,
                    'price': book.price
                })
        
        # Send purchase confirmation email to customer
        try:
            # Prepare discount information for email
            discount_info = None
            if discount_code and discount_amount > 0:
                discount_info = {
                    'code': discount_code,
                    'amount': discount_amount,
                    'final_total': total
                }
            
            send_customer_purchase_notification(
                customer_email=current_user.email,
                customer_name=current_user.full_name,
                purchase_details=purchase_details,
                transaction_id=payment_record.transaction_id,
                discount_info=discount_info
            )
        except Exception as e:
            print(f"Failed to send customer notification: {e}")
            # Don't fail the checkout if email fails
        
        # Send admin notification about new purchase
        try:
            # Get the first item for the basic notification (or create a summary)
            first_item = purchase_details[0] if purchase_details else None
            book_isbn_list = [isbn for isbn in cart.keys()]
            quantity_total = sum(cart.values())
            
            # Prepare order details for admin
            admin_order_details = {
                'id': payment_record.transaction_id,
                'customer_name': current_user.full_name,
                'customer_email': current_user.email,
                'customer_phone': current_user.phone or 'N/A',
                'book_isbn': ', '.join(book_isbn_list) if book_isbn_list else 'N/A',
                'quantity': quantity_total,
                'status': 'Confirmed',
                'payment_method': payment_method,
                'amount': total,
                'items_count': len(purchase_details),
                'timestamp': datetime.now().strftime('%B %d, %Y at %I:%M %p')
            }
            
            # Build items summary for admin
            items_summary = ""
            for item in purchase_details:
                items_summary += f"• {item['title']} (Qty: {item['quantity']}) - ${item['price']:.2f}\n"
            
            admin_message = f"""New purchase completed on Chapter 6: A Plot Twist Bookstore!

CUSTOMER INFORMATION:
Name: {current_user.full_name}
Email: {current_user.email}
Phone: {current_user.phone or 'N/A'}

TRANSACTION DETAILS:
Transaction ID: {payment_record.transaction_id}
Payment Method: {payment_method.replace('_', ' ').title()}
Total Amount: ${total:.2f}
Date: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}

ITEMS PURCHASED:
{items_summary}

This order requires processing and fulfillment."""

            send_admin_notification(
                subject=f"New Purchase - ${total:.2f} - {current_user.full_name}",
                message=admin_message,
                order_details=admin_order_details
            )
        except Exception as e:
            print(f"Failed to send admin notification: {e}")
            # Don't fail the checkout if email fails
        
        # Track used discount code to prevent reuse
        if discount_code:
            used_codes = session.get('used_discount_codes', [])
            used_codes.append(discount_code)
            session['used_discount_codes'] = used_codes
            # Clear current discount code
            session.pop('discount_code', None)
        
        # Clear cart
        session['cart'] = {}
        session.permanent = True
        
        flash(f"Payment successful! {payment_result}", "success")
        return redirect(url_for('receipt', amount=total, transaction_id=payment_record.transaction_id))
        
    except Exception as e:
        db.session.rollback()
        print(f"Exception in checkout processing: {str(e)}")
        flash(f"Error processing checkout: {e}", "danger")
    return redirect(url_for('checkout'))


@app.route('/test_route', methods=['GET', 'POST'])
def test_route():
    """Test route to verify Flask is working."""
    print("=== TEST ROUTE CALLED ===")
    if request.method == 'POST':
        print(f"POST data: {dict(request.form)}")
        return "POST received!"
    return "Test route works!"


@app.route('/simple_checkout_test')
def simple_checkout_test():
    """Simple checkout test page."""
    return render_template('test_checkout.html')

@app.route('/debug_checkout')
def debug_checkout():
    """Debug checkout page."""
    return render_template('debug_checkout.html')
    try:
        # Calculate subtotal first
        subtotal = 0
        for isbn, qty in cart.items():
            book = Book.query.filter_by(isbn=isbn).first()
            if book:
                # Check if enough inventory
                if book.quantity < qty:
                    flash(f"Not enough inventory for {book.title}. Only {book.quantity} available.", "danger")
                    return redirect(url_for('checkout'))
                subtotal += book.price * qty
        
        # Apply discount if applicable
        discount_code = session.get('discount_code')
        discount_amount = 0
        if discount_code and discount_code in DISCOUNT_CODES:
            discount_rate, min_order = DISCOUNT_CODES[discount_code]
            if subtotal >= min_order:
                discount_amount = subtotal * discount_rate
        
        total = subtotal - discount_amount
        
        # Process payment simulation
        try:
            payment_result = process_payment(total, payment_method, payment_details)
            flash(f"Payment successful! {payment_result}", "success")
        except PaymentError as e:
            error_type, user_message, suggested_action = handle_payment_error(e)
            flash(f"{user_message} {suggested_action}", error_type)
            return redirect(url_for('checkout'))
        
        # Create payment method record
        payment_record = PaymentMethod(
            method_type=payment_method,
            amount=total,
            status='completed'
        )
        
        # Store payment-specific information (secure way)
        if payment_method == 'credit_card':
            payment_record.card_last_four = payment_details['number'][-4:]
            payment_record.card_type = detect_card_type(payment_details['number'])
            payment_record.cardholder_name = payment_details['name']
        elif payment_method == 'paypal':
            payment_record.paypal_email = payment_details['email']
        elif payment_method == 'bank_transfer':
            payment_record.bank_name = payment_details['bank_name']
            payment_record.account_last_four = payment_details['account_number'][-4:]
        
        # Generate transaction ID
        payment_record.transaction_id = 'TXN' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        
        db.session.add(payment_record)
        
        # Process each item in cart
        for isbn, qty in cart.items():
            book = Book.query.filter_by(isbn=isbn).first()
            if book:
                # Calculate total price for this item (without discount - discount is applied to overall total)
                total_price = book.price * qty
                
                # Create sale record
                sale = Sale(book_id=isbn, quantity=qty, total_price=total_price)
                db.session.add(sale)
                
                # Create purchase record for logged-in customers
                purchase = Purchase(
                    customer_name=current_user.full_name,
                    customer_email=current_user.email,
                    customer_phone=current_user.phone,
                    customer_address=current_user.address_line1 or current_user.address,
                    book_isbn=isbn,
                    quantity=qty,
                    status='Confirmed'  # Set initial status
                )
                # Link payment to purchase
                purchase_id = db.session.flush()  # Get purchase ID
                payment_record.purchase_id = purchase.id if hasattr(purchase, 'id') else None
                
                db.session.add(purchase)
                
                # Update book inventory
                book.quantity -= qty
                if book.quantity == 0:
                    book.in_stock = False

        # Commit all changes
        db.session.commit()
        
        # Track used discount code to prevent reuse
        if discount_code:
            used_codes = session.get('used_discount_codes', [])
            used_codes.append(discount_code)
            session['used_discount_codes'] = used_codes
            # Clear current discount code
            session.pop('discount_code', None)
        
        # Clear cart
        session['cart'] = {}
        session.permanent = True
        
        return redirect(url_for('receipt', amount=total, transaction_id=payment_record.transaction_id))
        
    except Exception as e:
        db.session.rollback()
        flash(f"Error processing checkout: {e}", "danger")
        return redirect(url_for('checkout'))


@app.route('/receipt')
def receipt():
    """Display purchase receipt."""
    amount = request.args.get('amount', 0)
    transaction_id = request.args.get('transaction_id', 'N/A')
    return render_template('receipt.html', amount=amount, transaction_id=transaction_id)


# =============================================================================
# DISCOUNT CODE ROUTES
# =============================================================================

@app.route('/apply_discount', methods=['POST'])
def apply_discount():
    """Apply a discount code to the cart."""
    code = request.form.get('discount_code', '').strip().upper()
    cart = session.get('cart', {})
    subtotal = 0

    # Calculate subtotal to check minimum requirement
    for isbn, qty in cart.items():
        book = Book.query.filter_by(isbn=isbn).first()
        if book:
            subtotal += book.price * qty

    if code not in DISCOUNT_CODES:
        flash("Invalid discount code. Please check the spelling and try again.", 'danger')
        return redirect(url_for('view_cart'))

    discount_rate, min_order = DISCOUNT_CODES[code]

    # Check if code already used in this session
    used_codes = session.get('used_discount_codes', [])
    if code in used_codes:
        flash(f"The discount code '{code}' has already been used in this session.", 'warning')
        return redirect(url_for('view_cart'))

    # Check minimum order requirement with detailed message
    if subtotal < min_order:
        remaining_amount = min_order - subtotal
        flash(f"The discount code '{code}' requires a minimum order of ${min_order:.2f}. Your current subtotal is ${subtotal:.2f}. Please add ${remaining_amount:.2f} more to your cart to use this code.", 'warning')
        return redirect(url_for('view_cart'))

    # Apply the discount
    session['discount_code'] = code
    session.permanent = True
    discount_amount = subtotal * discount_rate
    flash(f"Success! Discount code '{code}' applied - {int(discount_rate*100)}% off (You saved ${discount_amount:.2f}!)", 'success')
    return redirect(url_for('view_cart'))


@app.route('/remove_discount')
def remove_discount():
    """Remove the current discount code."""
    if 'discount_code' in session:
        removed = session.pop('discount_code')
        session.permanent = True
        flash(f"Discount '{removed}' removed.", 'info')
    return redirect(url_for('view_cart'))


@app.route('/sales-report', methods=['GET', 'POST'])
@login_required
@manager_required
def sales_report():
    """Display sales report with date filtering."""
    sales = []
    
    if request.method == 'POST':
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        
        if start_date and end_date:
            # Convert to datetime objects for filtering
            start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
            end_datetime = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)  # Include end day
            
            # Get purchases from the Purchase table and create sale-like objects
            purchases = Purchase.query.filter(
                Purchase.timestamp >= start_datetime,
                Purchase.timestamp < end_datetime
            ).order_by(Purchase.timestamp.desc()).all()
            
            # Convert purchases to sale-like objects with calculated totals
            sales = []
            for purchase in purchases:
                # Find the book to get the price
                book = Book.query.filter_by(isbn=purchase.book_isbn).first()
                if book:
                    # Create a sale-like object
                    sale_obj = type('Sale', (), {})()
                    sale_obj.id = purchase.id
                    sale_obj.book_id = purchase.book_isbn
                    sale_obj.quantity = purchase.quantity
                    sale_obj.total_price = book.price * purchase.quantity
                    sale_obj.timestamp = purchase.timestamp
                    sales.append(sale_obj)
    
    return render_template('sales_report.html', sales=sales)


@app.route('/sales/export.csv')
@login_required
@manager_required
def export_sales_csv():
    """Export sales data to CSV file."""
    try:
        # Get date range from query parameters (optional)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Build query for purchases (which represent our sales)
        query = Purchase.query
        
        if start_date and end_date:
            start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
            end_datetime = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
            query = query.filter(
                Purchase.timestamp >= start_datetime,
                Purchase.timestamp < end_datetime
            )
        
        purchases = query.order_by(Purchase.timestamp.desc()).all()
        
        # Create CSV content
        csv_content = StringIO()
        writer = csv.writer(csv_content)
        
        # Write CSV header
        writer.writerow(['Sale ID', 'Book ISBN', 'Book Title', 'Author', 'Quantity', 'Unit Price', 'Total Price', 'Sale Date'])
        
        # Write sales data
        for purchase in purchases:
            book = Book.query.filter_by(isbn=purchase.book_isbn).first()
            if book:
                unit_price = book.price
                total_price = unit_price * purchase.quantity
                writer.writerow([
                    purchase.id,
                    purchase.book_isbn,
                    book.title,
                    book.author,
                    purchase.quantity,
                    f'{unit_price:.2f}',
                    f'{total_price:.2f}',
                    purchase.timestamp.strftime('%Y-%m-%d %H:%M:%S')
                ])
        
        # Create response
        csv_content.seek(0)
        
        # Generate filename with current timestamp
        filename = f"sales_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        response = Response(
            csv_content.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment; filename={filename}'}
        )
        
        return response
        
    except Exception as e:
        flash(f'Error exporting sales data: {str(e)}', 'danger')
        return redirect(url_for('sales_report'))


# Run the app
if __name__ == '__main__':
    with app.app_context():
        # ensure uploads dir exists inside instance
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        db.create_all()
    app.run(debug=True)
