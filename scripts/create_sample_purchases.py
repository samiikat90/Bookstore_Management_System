import sys
import os

ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app.app import app, db, Purchase


def main():
    """Seed the purchases table with a couple of example rows.

    Useful for manual testing of the manager purchases page without going
    through the full checkout flow. This simply inserts a couple of rows if
    the table exists (it will be created if necessary).
    """
    with app.app_context():
        db.create_all()
        samples = [
            dict(customer_name='Dana White', customer_email='dana@example.com', customer_phone='555-4444', customer_address='12 Birch St', book_isbn='9781001', quantity=1),
            dict(customer_name='Evan Brown', customer_email='evan@example.com', customer_phone='555-5555', customer_address='34 Cedar Ave', book_isbn='9781002', quantity=3),
        ]
        for s in samples:
            p = Purchase(**s)
            db.session.add(p)
        db.session.commit()
        print('Sample purchases created')


if __name__ == '__main__':
    main()
