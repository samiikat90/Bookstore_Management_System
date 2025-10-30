import os
import tempfile
import pytest
import uuid

from app.app import app, db, User, Purchase


@pytest.fixture
def client(tmp_path):
    db_fd, db_path = tempfile.mkstemp(dir=tmp_path, suffix='.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['TESTING'] = True
    with app.test_client() as client:
        import os
        import tempfile
        import pytest
        import uuid

        from app.app import app, db, User, Purchase


        @pytest.fixture
        def client(tmp_path):
            db_fd, db_path = tempfile.mkstemp(dir=tmp_path, suffix='.db')
            app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
            app.config['TESTING'] = True
            with app.test_client() as client:
                with app.app_context():
                    db.create_all()
                    # create a manager with unique username to avoid collisions
                    uname = f'mgr_{uuid.uuid4().hex[:8]}'
                    u = User(username=uname)
                    u.set_password('pw')
                    u.is_manager = True
                    db.session.add(u)
                    db.session.commit()
                    client.manager_username = uname
                yield client
            os.close(db_fd)
            os.remove(db_path)


        def login(client, username='mgr', password='pw'):
            return client.post('/login', data={'username': username, 'password': password}, follow_redirects=True)


        def test_protected_purchases_requires_login(client):
            rv = client.get('/purchases')
            assert rv.status_code in (302, 401)


        def test_login_and_access_purchases(client):
            login(client, client.manager_username)
            rv = client.get('/purchases')
            assert rv.status_code == 200


        def test_create_purchase_public(client):
            rv = client.post('/create_purchase', data={'customer_name':'T','book_isbn':'123','quantity':1}, follow_redirects=True)
            assert b'Purchase created' in rv.data


        def test_export_csv_requires_manager(client):
            rv = client.get('/purchases/export.csv')
            assert rv.status_code in (302, 401)
            login(client, client.manager_username)
            rv = client.get('/purchases/export.csv')
            assert rv.status_code == 200
            assert b'customer_name' in rv.data
