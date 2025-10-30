import sys
import os

# Ensure the project root is on sys.path so `app` package can be imported when
# running this script from the scripts/ directory.
ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app.app import app, db, User


def main():
    with app.app_context():
        db.create_all()
        try:
            users = User.query.all()
            print(f'TOTAL_USERS: {len(users)}')
            print('=' * 50)
            
            for user in users:
                print(f'ID: {user.id}')
                print(f'Username: {user.username}')
                print(f'Email: {user.email}')
                print(f'Full Name: {user.full_name}')
                print(f'Is Manager: {user.is_manager}')
                print(f'Receive Notifications: {user.receive_notifications}')
                print(f'Has Password Hash: {bool(user.password_hash)}')
                print(f'Has Legacy Password: {bool(user.password)}')
                print(f'2FA Code: {user.two_fa_code}')
                print(f'2FA Expires: {user.two_fa_expires}')
                print(f'2FA Verified: {user.two_fa_verified}')
                print('-' * 30)
                
        except Exception as e:
            print('QUERY_ERROR:', repr(e))

if __name__ == '__main__':
    main()