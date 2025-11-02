## Application entrypoint and main Flask app configuration.
##
## This file contains the Flask app, database models (Book, User, Purchase),
## authentication (Flask-Login) and manager-only routes for inventory and
## purchase review. Comments explain the purpose of each section.
from flask import Flask, request, render_template, redirect, url_for, flash, jsonify, make_response, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from functools import wraps
from sqlalchemy import text, union_all, or_
import os, json
import csv
import random
import string
import smtplib

# Initialize Flask app
app = Flask(__name__, instance_relative_config=True)
app.secret_key = 'your_secret_key'

# Configure session to expire when browser closes
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)  # Fallback timeout
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Security: prevent JavaScript access to session cookie
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # CSRF protection

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
    customer_email = db.Column(db.String(120))
    customer_phone = db.Column(db.String(50))
    customer_address = db.Column(db.Text)
    book_isbn = db.Column(db.String(50))
    quantity = db.Column(db.Integer, default=1)
    status = db.Column(db.String(50), default='Pending')
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    source = db.Column(db.String(20), default='purchase')  # indicate this is from purchases table


@login_manager.user_loader
def load_user(user_id):
    try:
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
    """Web view for catalog.csv with search and category filter."""
    catalog_file = os.path.join(app.root_path, '..', 'uploads', 'BookListing.csv')
    catalog = load_catalog(catalog_file)
    # Load inventory from Book model
    inventory_books = Book.query.all()
    inventory = []
    for book in inventory_books:
        inventory.append({
            'Name': book.title,
            'Category': getattr(book, 'cover_type', 'Inventory'),
            'Price': float(book.price),
            'Source': 'Inventory',
            'Author': book.author,
            'Quantity': book.quantity,
            'ISBN': book.isbn
        })
    # Add Source field to catalog items
    for item in catalog:
        item['Source'] = 'Catalog'
        item['Author'] = item.get('Author', '')
        item['Quantity'] = None
        item['ISBN'] = None
    # Remove items with 'Unknown' title from catalog
    catalog = [item for item in catalog if item['Name'] != 'Unknown']
    # Merge and deduplicate by Name+Category+Price
    all_items = catalog + inventory
    seen = set()
    merged = []
    for item in all_items:
        key = (item['Name'], item['Category'], item['Price'])
        if key not in seen:
            merged.append(item)
            seen.add(key)
    search = (request.args.get('search') or '').strip()
    category = (request.args.get('category') or '').strip()
    filtered = merged
    if search:
        filtered = [item for item in filtered if search.lower() in item['Name'].lower()]
    if category:
        filtered = [item for item in filtered if item['Category'] and item['Category'].lower() == category.lower()]
    categories = sorted(set(item['Category'] for item in merged if item['Category']))
    return render_template('catalog.html', catalog=filtered, search=search, category=category, categories=categories)


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

# Homepage route
@app.route('/')
@login_required
@manager_required
def index():
    # redirect managers to unified admin dashboard
    return redirect(url_for('admin_dashboard'))


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
                    order_list.append(f"Order #{update_info['order'].id}: {update_info['old_status']} → {update_info['new_status']}")
                
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
        return redirect(url_for('catalog_view'))
    except Exception as e:
        flash(f"Error adding book: {e}", 'danger')
        return redirect(url_for('add_book'))

    return redirect(url_for('catalog_view'))

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
            return redirect(url_for('catalog_view'))
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
            return redirect(url_for('catalog_view'))
        
        if quantity_to_delete > current_quantity:
            flash(f"Cannot delete {quantity_to_delete} copies - only {current_quantity} available.", 'danger')
            return redirect(url_for('catalog_view'))
        
        # Check if there are any pending orders for this book
        pending_orders = Purchase.query.filter_by(book_isbn=isbn, status='Pending').count()
        if pending_orders > 0 and quantity_to_delete >= current_quantity:
            flash(f"Cannot delete all copies of '{book_title}' - there are {pending_orders} pending orders for this book. Please fulfill or cancel the orders first.", 'warning')
            return redirect(url_for('catalog_view'))
        
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
    
    return redirect(url_for('catalog_view'))

# Mark book out of stock
@app.route('/mark_out_of_stock/<isbn>', methods=['POST'])
@login_required
@manager_required
def mark_out_of_stock(isbn):
    book = Book.query.get(isbn)
    if book:
        book.in_stock = False
        book.quantity = 0
        db.session.commit()
        flash(f"Book '{book.title}' marked out of stock.", 'warning')
    return redirect(url_for('index'))

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

    return redirect(url_for('catalog_view'))


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
        return redirect(url_for('catalog_view'))


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
            
            next_page = request.args.get('next') or url_for('index')
            return redirect(next_page)
        else:
            flash('Invalid security code. Please try again.', 'danger')
    
    return render_template('verify_2fa.html')


@app.route('/logout')
@login_required
def logout():
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


# Browse route for customer-facing book browsing
@app.route('/browse')
def browse():
    """Browse books with search functionality for customers."""
    search_query = request.args.get('q', '').strip()
    books = Book.query.filter_by(in_stock=True)
    
    if search_query:
        books = books.filter(
            or_(
                Book.title.contains(search_query),
                Book.author.contains(search_query),
                Book.isbn.contains(search_query)
            )
        )
    
    inventory = books.all()
    return render_template('browse.html', inventory=inventory, search_query=search_query)


# Cart routes
@app.route('/cart')
def view_cart():
    """View the shopping cart."""
    if 'cart' not in session:
        session['cart'] = []
    
    cart = session['cart']
    total = sum(item['price'] * item['quantity'] for item in cart)
    return render_template('cart.html', cart=cart, total=total)


@app.route('/add_to_cart/<isbn>', methods=['POST'])
def add_to_cart(isbn):
    """Add a book to the cart."""
    if 'cart' not in session:
        session['cart'] = []
    
    quantity = int(request.form.get('quantity', 1))
    book = Book.query.get(isbn)
    
    if not book or not book.in_stock:
        flash('Book not available.', 'danger')
        return redirect(url_for('browse'))
    
    cart = session['cart']
    
    # Check if book is already in cart
    for item in cart:
        if item['isbn'] == isbn:
            item['quantity'] += quantity
            break
    else:
        # Add new item to cart
        cart.append({
            'isbn': book.isbn,
            'title': book.title,
            'author': book.author,
            'price': book.price,
            'quantity': quantity
        })
    
    session['cart'] = cart
    flash(f'Added "{book.title}" to cart.', 'success')
    return redirect(url_for('browse'))


@app.route('/update_cart/<isbn>', methods=['POST'])
def update_cart(isbn):
    """Update quantity of an item in the cart."""
    if 'cart' not in session:
        session['cart'] = []
    
    new_quantity = int(request.form.get('quantity', 0))
    cart = session['cart']
    
    for item in cart:
        if item['isbn'] == isbn:
            if new_quantity <= 0:
                cart.remove(item)
                flash('Item removed from cart.', 'info')
            else:
                item['quantity'] = new_quantity
                flash('Cart updated.', 'info')
            break
    
    session['cart'] = cart
    return redirect(url_for('view_cart'))


@app.route('/remove_from_cart/<isbn>', methods=['POST'])
def remove_from_cart(isbn):
    """Remove an item from the cart."""
    if 'cart' not in session:
        session['cart'] = []
    
    cart = session['cart']
    cart = [item for item in cart if item['isbn'] != isbn]
    session['cart'] = cart
    
    flash('Item removed from cart.', 'info')
    return redirect(url_for('view_cart'))


@app.route('/reset_cart', methods=['POST'])
def reset_cart():
    """Clear all items from the cart."""
    session['cart'] = []
    flash('Cart cleared.', 'info')
    return redirect(url_for('view_cart'))


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


# Run the app
if __name__ == '__main__':
    with app.app_context():
        # ensure uploads dir exists inside instance
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        db.create_all()
    app.run(debug=True)