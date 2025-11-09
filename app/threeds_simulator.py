"""
3D Secure Authentication Simulation Module

This module simulates 3D Secure (3DS) authentication for credit card payments.
In a real implementation, this would integrate with actual 3DS providers like
Stripe 3DS, Adyen 3DS, or bank-specific 3DS services.
"""

import secrets
import random
from datetime import datetime, timedelta
from typing import Dict, Any, Tuple

class ThreeDSecureSimulator:
 """Simulates 3D Secure authentication process."""
 
 def __init__(self):
 self.challenge_sessions = {}
 
 def initiate_3ds_authentication(self, card_number: str, amount: float) -> Dict[str, Any]:
 """
 Initiate 3D Secure authentication for a card payment.
 
 Returns:
 Dictionary with authentication details
 """
 # Generate unique challenge session
 challenge_id = f"3DS_{secrets.token_hex(8).upper()}"
 
 # Determine if 3DS challenge is required (simulation logic)
 requires_challenge = self._should_require_challenge(card_number, amount)
 
 if requires_challenge:
 # Generate authentication challenge
 challenge_code = f"{random.randint(100000, 999999)}"
 
 self.challenge_sessions[challenge_id] = {
 'card_last_four': card_number[-4:],
 'amount': amount,
 'challenge_code': challenge_code,
 'created_at': datetime.now(),
 'expires_at': datetime.now() + timedelta(minutes=5),
 'attempts': 0,
 'status': 'pending'
 }
 
 return {
 'requires_challenge': True,
 'challenge_id': challenge_id,
 'challenge_method': 'SMS', # Simulated SMS challenge
 'challenge_code': challenge_code, # In real 3DS, this would be sent to user
 'message': f'3D Secure challenge initiated. Code sent to registered mobile number ending in **{random.randint(10, 99)}',
 'expires_in': 300 # 5 minutes
 }
 else:
 # Frictionless flow - no challenge required
 return {
 'requires_challenge': False,
 'challenge_id': challenge_id,
 'authentication_status': 'authenticated',
 'message': '3D Secure authentication completed (frictionless)'
 }
 
 def verify_3ds_challenge(self, challenge_id: str, provided_code: str) -> Dict[str, Any]:
 """
 Verify 3D Secure challenge response.
 
 Returns:
 Dictionary with verification result
 """
 if challenge_id not in self.challenge_sessions:
 return {
 'success': False,
 'error': 'Invalid or expired challenge session',
 'authentication_status': 'failed'
 }
 
 session = self.challenge_sessions[challenge_id]
 
 # Check if session has expired
 if datetime.now() > session['expires_at']:
 del self.challenge_sessions[challenge_id]
 return {
 'success': False,
 'error': '3D Secure challenge has expired',
 'authentication_status': 'expired'
 }
 
 # Increment attempts
 session['attempts'] += 1
 
 # Check attempt limit
 if session['attempts'] > 3:
 session['status'] = 'failed'
 return {
 'success': False,
 'error': 'Too many failed attempts',
 'authentication_status': 'failed'
 }
 
 # Verify challenge code
 if provided_code == session['challenge_code']:
 session['status'] = 'authenticated'
 
 # Generate authentication token
 auth_token = f"3DS_AUTH_{secrets.token_hex(12).upper()}"
 
 return {
 'success': True,
 'authentication_status': 'authenticated',
 'auth_token': auth_token,
 'message': '3D Secure authentication successful'
 }
 else:
 return {
 'success': False,
 'error': f'Incorrect challenge code. {3 - session["attempts"]} attempts remaining',
 'authentication_status': 'challenge_failed',
 'attempts_remaining': 3 - session['attempts']
 }
 
 def _should_require_challenge(self, card_number: str, amount: float) -> bool:
 """
 Determine if a transaction requires 3DS challenge based on risk factors.
 In real implementation, this would be based on:
 - Transaction amount
 - Merchant risk profile
 - User behavior patterns
 - Regulatory requirements (EU SCA)
 """
 # High-value transactions always require challenge
 if amount >= 500.0:
 return True
 
 # Simulate risk-based authentication
 # 70% of transactions under $100 are frictionless
 # Higher amounts have higher challenge rates
 if amount < 100:
 return random.random() > 0.7
 elif amount < 250:
 return random.random() > 0.4
 else:
 return random.random() > 0.2
 
 def get_challenge_status(self, challenge_id: str) -> Dict[str, Any]:
 """Get the current status of a 3DS challenge."""
 if challenge_id not in self.challenge_sessions:
 return {'error': 'Challenge session not found'}
 
 session = self.challenge_sessions[challenge_id]
 return {
 'status': session['status'],
 'expires_at': session['expires_at'].isoformat(),
 'attempts': session['attempts'],
 'time_remaining': max(0, (session['expires_at'] - datetime.now()).total_seconds())
 }

# Global 3DS simulator instance
threeds_simulator = ThreeDSecureSimulator()

def initiate_3ds_auth(card_number: str, amount: float) -> Dict[str, Any]:
 """Convenience function to initiate 3D Secure authentication."""
 return threeds_simulator.initiate_3ds_authentication(card_number, amount)

def verify_3ds_auth(challenge_id: str, code: str) -> Dict[str, Any]:
 """Convenience function to verify 3D Secure challenge."""
 return threeds_simulator.verify_3ds_challenge(challenge_id, code)

def check_3ds_status(challenge_id: str) -> Dict[str, Any]:
 """Convenience function to check 3DS challenge status."""
 return threeds_simulator.get_challenge_status(challenge_id)