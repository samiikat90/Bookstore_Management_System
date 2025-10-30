import sys
import os

ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app.app import app, db, Order


def main():
    """Create a few rows in the legacy `order` table for testing.

    This script uses the legacy Order model to insert representative rows
    into the old orders table. It's helpful when you want to exercise the
    import/migration path (copying legacy orders into the new `purchases`
    table) without having to recreate a full checkout flow.

    The script is intentionally idempotent for manual use: it will create
    the table if necessary and then insert the sample rows. If you run it
    multiple times you will get duplicate rows; use the import script's
    deduplication logic if you want to move them into `purchases` safely.
    """
    with app.app_context():
        # Ensure the tables exist (no-op if already created)
        db.create_all()

        samples = [
            dict(customer_name='Alice Johnson', customer_email='alice@example.com', customer_phone='555-1111', customer_address='123 Maple St', book_isbn='9780001', quantity=1),
            dict(customer_name='Bob Smith', customer_email='bob@example.com', customer_phone='555-2222', customer_address='456 Oak Ave', book_isbn='9780002', quantity=2),
            dict(customer_name='Carol Lee', customer_email='carol@example.com', customer_phone='555-3333', customer_address='789 Pine Rd', book_isbn='9780003', quantity=1),
        ]

        for s in samples:
            # Construct a legacy Order object and add to the session
            o = Order(**s)
            db.session.add(o)

        db.session.commit()
        print('Sample orders created')


if __name__ == '__main__':
    main()
