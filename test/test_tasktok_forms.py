# Unit tests for TaskTok\forms.py

import unittest
from flask import Flask
from TaskTok.forms import NewUserForm, validate_username
from wtforms import StringField, ValidationError

from TaskTok import app

class TestValidateUsername(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.ctx = app.app_context()
        self.ctx.push()
        self.request_ctx = app.test_request_context()
        self.request_ctx.push()
        self.form = NewUserForm()

    def tearDown(self):
        self.request_ctx.pop()
        self.ctx.pop()

    # U-4.1.1
    def test_username_too_short(self):
        self.form.username.data = 'bob'
        with self.assertRaises(ValidationError):
            validate_username(self.form, self.form.username)

    # U-4.1.2
    def test_username_too_long(self):
        self.form.username.data = 'VladimirovichBobonovska'
        with self.assertRaises(ValidationError):
            validate_username(self.form, self.form.username)

    # U-4.1.3
    def test_username_all_numbers(self):
        self.form.username.data = '12345'
        with self.assertRaises(ValidationError):
            validate_username(self.form, self.form.username)

    # U-4.1.4
    def test_username_invalid_characters(self):
        self.form.username.data = 'Bob$350'
        with self.assertRaises(ValidationError):
            validate_username(self.form, self.form.username)

    # U-4.1.5
    def test_valid_username(self):
        self.form.username.data = 'validuser123'
        try:
            validate_username(self.form, self.form.username)
        except ValidationError:
            self.fail("validate_username raised ValidationError")

if __name__ == '__main__':
    unittest.main()