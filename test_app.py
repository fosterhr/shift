import pytest
import json
from flask import Flask
from app import app, db, User
import bcrypt

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///:memory:"
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.drop_all()

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