import sys
import os

# Ensure the project root is on sys.path so `app` package can be imported when
# running this script from the scripts/ directory.
ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app.app import app, db, Book


def main():
    with app.app_context():
        db.create_all()
        try:
            count = Book.query.count()
            print('BOOK_COUNT:', count)
        except Exception as e:
            print('QUERY_ERROR:', repr(e))

    print('INSTANCE_PATH:', app.instance_path)
    print('UPLOADS_PATH:', app.config.get('UPLOAD_FOLDER'))
    print('DB_URI:', app.config.get('SQLALCHEMY_DATABASE_URI'))

if __name__ == '__main__':
    main()
