#!/usr/bin/env python3

"""
Test the updated admin dashboard pending count logic
"""

import os
import sys

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app import app, db, Purchase

def test_admin_dashboard_count():
	"""Test the new admin dashboard pending count"""
	print("=== Testing Updated Admin Dashboard Count ===")
	
	with app.app_context():
		# Old method (only Pending)
		old_pending_count = Purchase.query.filter_by(status='Pending').count()
		print(f"Old method (Pending only): {old_pending_count}")
		
		# New method (Pending, Confirmed, Processing)
		new_pending_count = Purchase.query.filter(Purchase.status.in_(['Pending', 'Confirmed', 'Processing'])).count()
		print(f"New method (Pending + Confirmed + Processing): {new_pending_count}")
		
		# Show breakdown
		print("\nBreakdown:")
		for status in ['Pending', 'Confirmed', 'Processing']:
			count = Purchase.query.filter_by(status=status).count()
			print(f" {status}: {count}")
		
		print(f"\nDifference: {new_pending_count - old_pending_count} more orders need attention")

if __name__ == "__main__":
 test_admin_dashboard_count()