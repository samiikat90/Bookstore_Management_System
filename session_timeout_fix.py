# Session Timeout Fix Implementation
# 
# This file contains a properly implemented session timeout system
# that can replace the current implementation when needed.

from datetime import datetime, timedelta
from flask import session, current_app
from flask_login import current_user

def init_session_timeout():
 """Initialize session timeout for a new user session."""
 session['last_activity'] = datetime.utcnow().isoformat()
 session.permanent = True

def update_session_activity():
 """Update the last activity timestamp."""
 session['last_activity'] = datetime.utcnow().isoformat()

def check_session_timeout_fixed():
 """
 Fixed version of session timeout check.
 Returns True if session has timed out, False otherwise.
 """
 # Only check timeout for authenticated admin users
 if not (current_user.is_authenticated and hasattr(current_user, 'is_manager') and current_user.is_manager):
 return False
 
 last_activity_str = session.get('last_activity')
 
 # If no last activity recorded, consider it fresh session
 if not last_activity_str:
 init_session_timeout()
 return False
 
 try:
 last_activity = datetime.fromisoformat(last_activity_str)
 current_time = datetime.utcnow()
 time_since_activity = current_time - last_activity
 
 # Debug logging (remove in production)
 current_app.logger.debug(f"Session check: Last activity {last_activity}, Current time {current_time}, Time since: {time_since_activity}")
 
 # Check if timeout exceeded
 timeout_limit = timedelta(hours=2) # 2 hour timeout
 if time_since_activity > timeout_limit:
 current_app.logger.info(f"Session timed out for user {current_user.username}")
 return True
 
 return False
 
 except (ValueError, TypeError) as e:
 # If timestamp parsing fails, reset session
 current_app.logger.warning(f"Session timestamp parsing failed: {e}")
 init_session_timeout()
 return False

# Manager decorator with fixed session timeout
def manager_required_fixed(func):
 """Fixed version of manager_required decorator."""
 from functools import wraps
 from flask import flash, redirect, url_for
 from flask_login import logout_user
 
 @wraps(func)
 def wrapper(*args, **kwargs):
 # Check authentication first
 if not current_user.is_authenticated:
 return redirect(url_for('login'))
 
 # Check manager status
 if not getattr(current_user, 'is_manager', False):
 flash('Manager access required', 'danger')
 return redirect(url_for('login'))
 
 # Update activity BEFORE checking timeout
 update_session_activity()
 
 # Check for session timeout (with updated activity)
 if check_session_timeout_fixed():
 logout_user()
 session.clear()
 flash('Your session has expired due to inactivity. Please login again.', 'warning')
 return redirect(url_for('login'))
 
 return func(*args, **kwargs)
 
 return wrapper