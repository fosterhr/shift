import pytest
from app import app, db, User
import bcrypt
import tempfile

@pytest.fixture
def client():
    # Create a temporary file to use for the SQLite database
    db_fd, db_path = tempfile.mkstemp()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"
    
    with app.app_context():
        db.create_all()  # Create the database tables
        yield app.test_client()  # This is the test client
        db.drop_all()  # Clean up after tests
    # Close and remove the temporary database file
    os.close(db_fd)
    os.remove(db_path)

def test_register(client):
    response = client.post('/register', data={
        'email': 'test@example.com',
        'password': 'password123',
        'confirm_password': 'password123'
    })
    assert response.status_code == 302 
    user = User.query.filter_by(email='test@example.com').first()
    assert user is not None
    assert bcrypt.checkpw('password123'.encode('utf-8'), user.password.encode('utf-8'))

def test_login(client):
    # First, register a user
    client.post('/register', data={
        'email': 'test@example.com',
        'password': 'password123',
        'confirm_password': 'password123'
    })

    # Now log in
    response = client.post('/login', data={
        'email': 'test@example.com',
        'password': 'password123'
    })
    assert response.status_code == 302  # Ensure the response is a redirect

    # Follow the redirect to the account page
    response = client.get('/account')  # This will follow the redirect automatically

    # Check if user is logged in by checking the content of the account page
    assert b'Account' in response.data  # Adjust this to check the actual content of your account page

def test_account_access(client):
    # First, register and log in a user
    client.post('/register', data={
        'email': 'test@example.com',
        'password': 'password123',
        'confirm_password': 'password123'
    })
    client.post('/login', data={
        'email': 'test@example.com',
        'password': 'password123'
    })
    
    response = client.get('/account')
    assert response.status_code == 200

def test_logout(client):
    client.post('/register', data={
        'email': 'test@example.com',
        'password': 'password123',
        'confirm_password': 'password123'
    })
    client.post('/login', data={
        'email': 'test@example.com',
        'password': 'password123'
    })
    
    response = client.get('/logout')
    assert response.status_code == 302

    response = client.get('/account')
    assert response.status_code == 302

if __name__ == "__main__":
    pytest.main()
