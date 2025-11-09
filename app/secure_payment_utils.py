"""
Enhanced Secure Payment Utilities Module

This module provides PCI DSS compliant payment handling including:
- No storage of full credit card numbers or CVV codes
- Data encryption and tokenization
- Secure audit logging
- Enhanced fraud detection
- Input sanitization and validation
"""

import re
import hashlib
import secrets
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple, List
from cryptography.fernet import Fernet
import logging

# =============================================================================
# SECURE LOGGING CONFIGURATION
# =============================================================================

# Configure secure payment logger
payment_logger = logging.getLogger('secure_payments')
payment_handler = logging.FileHandler('logs/secure_payments.log')
payment_handler.setFormatter(logging.Formatter(
 '%(asctime)s - %(levelname)s - [%(name)s] - %(message)s'
))
payment_logger.addHandler(payment_handler)
payment_logger.setLevel(logging.INFO)

# =============================================================================
# SECURITY CONSTANTS AND CONFIGURATION
# =============================================================================

# PCI DSS Compliance Settings
MAX_PAYMENT_ATTEMPTS = 3
PAYMENT_ATTEMPT_WINDOW = 300 # 5 minutes in seconds
RATE_LIMIT_WINDOW = 3600 # 1 hour in seconds
MAX_TRANSACTIONS_PER_HOUR = 20

# Fraud Detection Thresholds
SUSPICIOUS_AMOUNT_THRESHOLD = 1000.0 # Amounts over $1000 are flagged
VELOCITY_CHECK_THRESHOLD = 5 # Max 5 transactions per 10 minutes

# =============================================================================
# PAYMENT DATA ENCRYPTION AND TOKENIZATION
# =============================================================================

class SecurePaymentHandler:
 """Handles secure payment processing with PCI DSS compliance."""
 
 def __init__(self, encryption_key: Optional[bytes] = None):
 """Initialize with encryption key for sensitive data."""
 if encryption_key is None:
 # In production, this should come from environment variables
 encryption_key = Fernet.generate_key()
 self.cipher = Fernet(encryption_key)
 
 # Track payment attempts for rate limiting
 self.payment_attempts = {}
 self.transaction_history = {}
 
 def sanitize_payment_input(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
 """
 Sanitize and validate payment input data to prevent injection attacks.
 """
 sanitized = {}
 
 # Sanitize common payment fields
 if 'card_number' in payment_data:
 # Remove all non-digits and validate format
 card_num = re.sub(r'[^\d]', '', str(payment_data['card_number']))
 if 13 <= len(card_num) <= 19:
 sanitized['card_number'] = card_num
 else:
 raise ValueError("Invalid card number format")
 
 if 'cvv' in payment_data:
 cvv = re.sub(r'[^\d]', '', str(payment_data['cvv']))
 if 3 <= len(cvv) <= 4:
 sanitized['cvv'] = cvv
 else:
 raise ValueError("Invalid CVV format")
 
 if 'expiry' in payment_data:
 # Validate MM/YY format
 expiry = str(payment_data['expiry']).strip()
 if re.match(r'^\d{2}/\d{2}$', expiry):
 sanitized['expiry'] = expiry
 else:
 raise ValueError("Invalid expiry date format (MM/YY required)")
 
 if 'cardholder_name' in payment_data:
 # Allow only letters, spaces, hyphens, apostrophes
 name = re.sub(r'[^a-zA-Z\s\-\']', '', str(payment_data['cardholder_name']))
 if len(name.strip()) > 0:
 sanitized['cardholder_name'] = name.strip().title()
 else:
 raise ValueError("Invalid cardholder name")
 
 if 'email' in payment_data:
 email = str(payment_data['email']).strip().lower()
 email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
 if re.match(email_pattern, email):
 sanitized['email'] = email
 else:
 raise ValueError("Invalid email format")
 
 if 'amount' in payment_data:
 try:
 amount = float(payment_data['amount'])
 if amount > 0:
 sanitized['amount'] = round(amount, 2)
 else:
 raise ValueError("Amount must be positive")
 except (ValueError, TypeError):
 raise ValueError("Invalid amount format")
 
 return sanitized
 
 def generate_payment_token(self, card_number: str) -> str:
 """
 Generate a secure token for the card number instead of storing the full number.
 """
 # Create a hash of the card number with a secret salt
 salt = secrets.token_hex(16)
 card_hash = hashlib.sha256((card_number + salt).encode()).hexdigest()
 
 # Create a token format: TOKEN_[first4][last4]_[hash_prefix]
 token = f"TOKEN_{card_number[:4]}{card_number[-4:]}_{card_hash[:8].upper()}"
 
 # Log token generation (without sensitive data)
 payment_logger.info(f"Payment token generated: {token}")
 
 return token
 
 def encrypt_sensitive_data(self, data: str) -> str:
 """Encrypt sensitive payment data."""
 return self.cipher.encrypt(data.encode()).decode()
 
 def decrypt_sensitive_data(self, encrypted_data: str) -> str:
 """Decrypt sensitive payment data."""
 return self.cipher.decrypt(encrypted_data.encode()).decode()
 
 def check_rate_limiting(self, client_ip: str) -> Tuple[bool, str]:
 """
 Check if client has exceeded rate limits for payment attempts.
 
 Returns:
 Tuple of (is_allowed, message)
 """
 current_time = time.time()
 
 if client_ip not in self.payment_attempts:
 self.payment_attempts[client_ip] = []
 
 # Clean old attempts outside the window
 self.payment_attempts[client_ip] = [
 attempt_time for attempt_time in self.payment_attempts[client_ip]
 if current_time - attempt_time < RATE_LIMIT_WINDOW
 ]
 
 # Check if limit exceeded
 if len(self.payment_attempts[client_ip]) >= MAX_TRANSACTIONS_PER_HOUR:
 return False, f"Rate limit exceeded. Maximum {MAX_TRANSACTIONS_PER_HOUR} transactions per hour allowed."
 
 # Add current attempt
 self.payment_attempts[client_ip].append(current_time)
 
 return True, "Rate limit check passed"
 
 def detect_fraud_indicators(self, payment_data: Dict[str, Any], client_ip: str) -> List[str]:
 """
 Detect potential fraud indicators in payment data.
 
 Returns:
 List of fraud warning messages
 """
 warnings = []
 
 # High amount transaction
 if payment_data.get('amount', 0) > SUSPICIOUS_AMOUNT_THRESHOLD:
 warnings.append(f"High amount transaction: ${payment_data['amount']}")
 
 # Velocity check - multiple transactions in short time
 current_time = time.time()
 if client_ip in self.transaction_history:
 recent_transactions = [
 t for t in self.transaction_history[client_ip]
 if current_time - t < 600 # 10 minutes
 ]
 if len(recent_transactions) >= VELOCITY_CHECK_THRESHOLD:
 warnings.append("High transaction velocity detected")
 else:
 self.transaction_history[client_ip] = []
 
 # Add current transaction to history
 self.transaction_history[client_ip].append(current_time)
 
 # Check for suspicious card patterns
 if 'card_number' in payment_data:
 card_num = payment_data['card_number']
 
 # Sequential numbers (potential test cards)
 if len(set(card_num[-4:])) == 1: # All same digits in last 4
 warnings.append("Suspicious card number pattern detected")
 
 # Common test card numbers
 test_cards = ['4111111111111111', '5555555555554444', '378282246310005']
 if card_num in test_cards:
 warnings.append("Test card number detected")
 
 return warnings
 
 def create_secure_payment_record(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
 """
 Create a secure payment record that complies with PCI DSS.
 Does not store full card numbers or CVV codes.
 """
 secure_record = {
 'timestamp': datetime.now().isoformat(),
 'payment_method': payment_data.get('method_type', 'unknown'),
 'amount': payment_data.get('amount', 0.0),
 'currency': 'USD',
 'status': 'pending'
 }
 
 if payment_data.get('method_type') == 'credit_card':
 # Store only last 4 digits and card type - NEVER the full number
 card_number = payment_data.get('card_number', '')
 secure_record.update({
 'card_last_four': card_number[-4:] if card_number else None,
 'card_type': self._detect_card_type(card_number),
 'cardholder_name': payment_data.get('cardholder_name', ''),
 'payment_token': self.generate_payment_token(card_number) if card_number else None
 })
 
 # NEVER store CVV - it's validation only
 
 elif payment_data.get('method_type') == 'paypal':
 secure_record.update({
 'paypal_email': payment_data.get('email', '')
 })
 
 elif payment_data.get('method_type') == 'bank_transfer':
 account_number = payment_data.get('account_number', '')
 secure_record.update({
 'bank_name': payment_data.get('bank_name', ''),
 'account_last_four': account_number[-4:] if account_number else None
 })
 
 return secure_record
 
 def _detect_card_type(self, card_number: str) -> str:
 """Detect card type from card number."""
 if not card_number:
 return "Unknown"
 
 if card_number.startswith('4'):
 return "Visa"
 elif card_number.startswith(('51', '52', '53', '54', '55')):
 return "Mastercard"
 elif card_number.startswith(('34', '37')):
 return "American Express"
 elif card_number.startswith('6011') or card_number.startswith('65'):
 return "Discover"
 else:
 return "Unknown"
 
 def log_payment_attempt(self, payment_data: Dict[str, Any], client_ip: str, 
 result: str, error_msg: Optional[str] = None):
 """
 Log payment attempt securely without exposing sensitive data.
 """
 log_entry = {
 'timestamp': datetime.now().isoformat(),
 'client_ip': client_ip,
 'payment_method': payment_data.get('method_type', 'unknown'),
 'amount': payment_data.get('amount', 0.0),
 'result': result,
 'error': error_msg
 }
 
 # Add non-sensitive identifiers
 if payment_data.get('method_type') == 'credit_card' and 'card_number' in payment_data:
 log_entry['card_last_four'] = payment_data['card_number'][-4:]
 log_entry['card_type'] = self._detect_card_type(payment_data['card_number'])
 
 if result == 'success':
 payment_logger.info(f"Payment successful: {log_entry}")
 else:
 payment_logger.warning(f"Payment failed: {log_entry}")

# =============================================================================
# CSRF PROTECTION FOR PAYMENT FORMS
# =============================================================================

def generate_csrf_token() -> str:
 """Generate a secure CSRF token for payment forms."""
 return secrets.token_urlsafe(32)

def validate_csrf_token(provided_token: str, session_token: str) -> bool:
 """Validate CSRF token to prevent cross-site request forgery."""
 return secrets.compare_digest(provided_token, session_token)

# =============================================================================
# ENHANCED PAYMENT VALIDATION
# =============================================================================

def enhanced_luhn_check(card_number: str) -> Tuple[bool, str]:
 """
 Enhanced Luhn algorithm check with detailed validation.
 
 Returns:
 Tuple of (is_valid, message)
 """
 # Remove spaces and non-digits
 digits = ''.join(filter(str.isdigit, card_number))
 
 if not digits:
 return False, "Card number cannot be empty"
 
 if len(digits) < 13:
 return False, "Card number is too short (minimum 13 digits)"
 
 if len(digits) > 19:
 return False, "Card number is too long (maximum 19 digits)"
 
 # Luhn algorithm implementation
 def luhn_checksum(card_num):
 def digits_of(n):
 return [int(d) for d in str(n)]
 
 digits = digits_of(card_num)
 odd_digits = digits[-1::-2]
 even_digits = digits[-2::-2]
 checksum = sum(odd_digits)
 for d in even_digits:
 checksum += sum(digits_of(d*2))
 return checksum % 10
 
 if luhn_checksum(digits) == 0:
 return True, "Card number is valid"
 else:
 return False, "Card number failed validation check (invalid checksum)"

def validate_expiry_date(expiry: str) -> Tuple[bool, str]:
 """
 Validate credit card expiry date.
 
 Returns:
 Tuple of (is_valid, message)
 """
 if not re.match(r'^\d{2}/\d{2}$', expiry):
 return False, "Expiry date must be in MM/YY format"
 
 try:
 month, year = map(int, expiry.split('/'))
 
 if month < 1 or month > 12:
 return False, "Invalid month (must be 01-12)"
 
 # Assume 20XX for years
 full_year = 2000 + year
 current_year = datetime.now().year
 current_month = datetime.now().month
 
 if full_year < current_year or (full_year == current_year and month < current_month):
 return False, "Card has expired"
 
 if full_year > current_year + 20: # Cards typically valid for max 20 years
 return False, "Invalid expiry date (too far in future)"
 
 return True, "Expiry date is valid"
 
 except ValueError:
 return False, "Invalid expiry date format"

def validate_cvv(cvv: str, card_type: str = "Unknown") -> Tuple[bool, str]:
 """
 Validate CVV code based on card type.
 
 Returns:
 Tuple of (is_valid, message)
 """
 if not cvv.isdigit():
 return False, "CVV must contain only digits"
 
 cvv_length = len(cvv)
 
 if card_type == "American Express":
 if cvv_length == 4:
 return True, "CVV is valid"
 else:
 return False, "American Express CVV must be 4 digits"
 else:
 if cvv_length == 3:
 return True, "CVV is valid"
 else:
 return False, "CVV must be 3 digits"

# =============================================================================
# SECURE PAYMENT PROCESSING
# =============================================================================

def process_secure_payment(amount: float, payment_data: Dict[str, Any], 
 client_ip: str, session_id: str) -> Dict[str, Any]:
 """
 Process payment with enhanced security measures.
 
 Returns:
 Dictionary with payment result and security information
 """
 handler = SecurePaymentHandler()
 
 try:
 # Step 1: Rate limiting check
 rate_check, rate_msg = handler.check_rate_limiting(client_ip)
 if not rate_check:
 raise SecurityError(f"Rate limit exceeded: {rate_msg}")
 
 # Step 2: Input sanitization
 sanitized_data = handler.sanitize_payment_input(payment_data)
 sanitized_data['amount'] = amount
 
 # Step 3: Fraud detection
 fraud_warnings = handler.detect_fraud_indicators(sanitized_data, client_ip)
 
 # Step 4: Payment validation
 method_type = sanitized_data.get('method_type', '').lower()
 
 if method_type == 'credit_card':
 # Validate card number
 card_valid, card_msg = enhanced_luhn_check(sanitized_data['card_number'])
 if not card_valid:
 raise PaymentValidationError(f"Card validation failed: {card_msg}")
 
 # Validate expiry
 expiry_valid, expiry_msg = validate_expiry_date(sanitized_data['expiry'])
 if not expiry_valid:
 raise PaymentValidationError(f"Expiry validation failed: {expiry_msg}")
 
 # Validate CVV
 card_type = handler._detect_card_type(sanitized_data['card_number'])
 cvv_valid, cvv_msg = validate_cvv(sanitized_data['cvv'], card_type)
 if not cvv_valid:
 raise PaymentValidationError(f"CVV validation failed: {cvv_msg}")
 
 # Step 5: Create secure payment record (PCI compliant)
 secure_record = handler.create_secure_payment_record(sanitized_data)
 
 # Step 6: Log payment attempt
 handler.log_payment_attempt(sanitized_data, client_ip, 'success')
 
 # Step 7: Generate transaction ID
 transaction_id = f"TXN_{secrets.token_hex(8).upper()}"
 
 result = {
 'success': True,
 'transaction_id': transaction_id,
 'secure_record': secure_record,
 'fraud_warnings': fraud_warnings,
 'message': 'Payment processed successfully'
 }
 
 if fraud_warnings:
 result['requires_review'] = True
 payment_logger.warning(f"Fraud indicators detected for transaction {transaction_id}: {fraud_warnings}")
 
 return result
 
 except Exception as e:
 # Log failed attempt
 handler.log_payment_attempt(payment_data, client_ip, 'failed', str(e))
 
 return {
 'success': False,
 'error': str(e),
 'error_type': type(e).__name__,
 'message': 'Payment processing failed'
 }

# =============================================================================
# CUSTOM SECURITY EXCEPTIONS
# =============================================================================

class SecurityError(Exception):
 """Raised for security-related payment issues."""
 pass

class PaymentValidationError(Exception):
 """Raised for payment validation failures."""
 pass

class RateLimitExceededError(SecurityError):
 """Raised when rate limits are exceeded."""
 pass