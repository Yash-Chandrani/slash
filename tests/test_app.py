import pytest
from src.modules.app import app, db, Users


@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_users.db'  # Use a test database
    client = app.test_client()
    with app.app_context():
        db.create_all()  # Create the test database
        yield client
        db.session.remove()
        db.drop_all()  # Clean up the test database


def test_database_connection(client):
    # Test the database connection by adding a sample user
    user = Users(name='John', email='john@example.com', passwordInput='password123')
    db.session.add(user)
    db.session.commit()

    # Retrieve the user from the test database
    retrieved_user = Users.query.filter_by(email='john@example.com').first()
    assert retrieved_user is not None


def test_user_registration(client):
    # Test user registration logic
    response = client.post('/register', data=dict(
        name='NewUser',
        email='newuser@example.com',
        password1='newpassword',
        password2='newpassword'
    ), follow_redirects=True)

    # Check if the registration was successful by looking for a flash message
    assert b'Registered successfully! Login to create wishlists' in response.data

def test_user_login(client):
    # Test user login logic
    response = client.post('/login', data=dict(
        email='john@example.com',
        password='password123'
    ), follow_redirects=True)

    # Check if the login was successful by looking for a flash message
    assert b'Success! You are logged in as: john@example.com' in response.data

def test_user_logout(client):
    # Test user logout logic
    response = client.get('/logout', follow_redirects=True)

    assert b'You have been logged out!' in response.data

def test_user_registration_existing_email(client):
    # Test user registration with an existing email address
    response = client.post('/register', data=dict(
        name='ExistingUser',
        email='john@example.com',  # Use an email that already exists
        password1='newpassword',
        password2='newpassword'
    ), follow_redirects=True)

    # Check if the registration fails with an error message
    assert b'An account with this email already exists' in response.data

def test_user_login_invalid_credentials(client):
    # Test user login with invalid credentials
    response = client.post('/login', data=dict(
        email='nonexistent@example.com',  # Use an email that doesn't exist
        password='invalidpassword'
    ), follow_redirects=True)

    # Check if the login fails with an error message
    assert b'Email or password do not match! Please try again' in response.data

def test_user_login_blank_fields(client):
    # Test user login with blank email and password fields
    response = client.post('/login', data=dict(
        email='',
        password=''
    ), follow_redirects=True)

    # Check if the login fails with an error message
    assert b'Email or password do not match! Please try again' in response.data
