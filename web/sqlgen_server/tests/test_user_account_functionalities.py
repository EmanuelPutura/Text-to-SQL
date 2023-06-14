import unittest
from flask import Flask, request, jsonify, make_response
from werkzeug.security import generate_password_hash

from web.sqlgen_server.app import app, db, User


class TestUserAccountFunctionalities(unittest.TestCase):
    def setUp(self):
        app.testing = True
        self.app = app.test_client()
        self.ctx = app.app_context()
        self.ctx.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def test_register_successful(self):
        payload = {
            'firstName': 'John',
            'lastName': 'Doe',
            'username': 'johndoe',
            'password': 'password123'
        }

        response = self.app.post('/users/register', json=payload)

        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertEqual(data['status'], 'registered')
        self.assertEqual(data['message'], "Successfully registered user 'johndoe'.")

    def test_register_missing_fields(self):
        payload = {
            'firstName': 'John',
            'lastName': 'Doe',
            # Missing 'username' field
            'password': 'password123'
        }

        response = self.app.post('/users/register', json=payload)

        self.assertEqual(response.status_code, 400)

    def test_register_existing_user(self):
        # Create a test user
        user = User(
            username='johndoe',
            first_name='John',
            last_name='Doe',
            password=generate_password_hash('password123')
        )
        db.session.add(user)
        db.session.commit()

        payload = {
            'firstName': 'John',
            'lastName': 'Doe',
            'username': 'johndoe',
            'password': 'password123'
        }

        response = self.app.post('/users/register', json=payload)

        self.assertEqual(response.status_code, 202)
        data = response.get_json()
        self.assertEqual(data['status'], 'already_registered')
        self.assertEqual(data['message'], "User 'johndoe' already exists, please log in.")

    def test_login_successful(self):
        # Create a test user
        user = User(
            username='johndoe',
            first_name='John',
            last_name='Doe',
            password=generate_password_hash('password123')
        )
        db.session.add(user)
        db.session.commit()

        payload = {
            'username': 'johndoe',
            'password': 'password123'
        }

        response = self.app.post('/users/authenticate', json=payload)

        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertEqual(data['username'], 'johndoe')
        self.assertEqual(data['firstName'], 'John')
        self.assertEqual(data['lastName'], 'Doe')
        self.assertTrue('token' in data)

    def test_login_invalid_password(self):
        # Create a test user
        user = User(
            username='johndoe',
            first_name='John',
            last_name='Doe',
            password=generate_password_hash('password123')
        )
        db.session.add(user)
        db.session.commit()

        payload = {
            'username': 'johndoe',
            'password': 'incorrectpassword'
        }

        response = self.app.post('/users/authenticate', json=payload)

        self.assertEqual(response.status_code, 403)
        data = response.get_json()
        self.assertEqual(data['status'], 'invalid_password')
        self.assertEqual(data['message'], 'Invalid password.')

    def test_login_unregistered_user(self):
        payload = {
            'username': 'unknownuser',
            'password': 'password123'
        }

        response = self.app.post('/users/authenticate', json=payload)

        self.assertEqual(response.status_code, 401)
        data = response.get_json()
        self.assertEqual(data['status'], 'unregistered_user')
        self.assertEqual(data['message'], "User 'unknownuser' does not exist.")
