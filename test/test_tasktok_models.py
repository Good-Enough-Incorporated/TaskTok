# Unit tests for TaskTok\models.py

import unittest
from unittest.mock import patch, MagicMock
import uuid
from TaskTok.models import User, NoNoTokens, TaskReminder
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from TaskTok.extensions import db, jwtManager

db_session_mock = patch('TaskTok.extensions.db.session').start()

class TestUserModel(unittest.TestCase):

    # U-6.1
    @patch('uuid.uuid4')
    def test_generate_uuid(self, mock_uuid4):
        generated_uuid = User.generate_uuid()
        val = uuid.UUID(generated_uuid, version=4)
        self.assertTrue(isinstance(val, uuid.UUID))
        self.assertEqual(val.version, 4)

    # U-6.2
    def test_repr(self):
        user = User(username='testuser')
        self.assertEqual(user.__repr__(), '<User testuser>')

    # U-6.3
    def test_set_password(self):
        user = User()
        user.set_password('password')
        self.assertIsNotNone(user.password)
        self.assertNotEqual(user.password, 'password')
        self.assertIsInstance(user.password, str)

    # U-6.4.1
    def test_verify_password_true(self):
        user = User()
        user.password = generate_password_hash('password')
        self.assertTrue(user.verify_password('password'))
        self.assertFalse(user.verify_password('notthepassword'))

    # U-6.4.2
    def test_verify_password_false(self):
        user = User()
        user.password = generate_password_hash('password')
        self.assertFalse(user.verify_password('notthepassword'))

    # U-6.5
    def test_verify_email_address(self):
        user = User()
        user.verify_email_address()
        self.assertTrue(user.is_confirmed)
        self.assertIsNotNone(user.confirmed_date)

    # U-6.6.1
    def test_is_account_verified_true(self):
        user = User()
        user.is_confirmed = True
        self.assertTrue(user.is_account_verified())

    # U-6.6.2
    def test_is_account_verified_false(self):
        user = User()
        self.assertFalse(user.is_account_verified())

    # U-6.7
    @patch('TaskTok.extensions.db.Model.query')
    def test_get_user_by_username(self, mock_query):
        User.get_user_by_username('testuser')
        mock_query.filter_by.assert_called_with(username='testuser')

    # U-6.8
    @patch('TaskTok.extensions.db.Model.query')
    def test_search_email_address(self, mock_query):
        User.search_email_address('user@TaskTok.com')
        mock_query.filter_by.assert_called_with(email='user@TaskTok.com')

    # U-6.9
    @patch('TaskTok.extensions.db.Model.query')
    def test_get_user_by_id(self, mock_query):
        User.get_user_by_id('123')
        mock_query.filter_by.assert_called_with(id='123')

    # U-6.10
    @patch('TaskTok.extensions.db.Model.query')
    def test_get_user_count(self, mock_query):
        User.get_user_count()
        mock_query.count.assert_called()

    # U-6.11
    def test_add(self):
        user = User()
        user.add()
        db_session_mock.add.assert_called_with(user)
        db_session_mock.commit.assert_called()

    # U-6.12
    def test_remove(self):
        user = User()
        user.remove()
        db_session_mock.delete.assert_called_with(user)
        db_session_mock.commit.assert_called()

class TestNoNoTokensModel(unittest.TestCase):

    # U-6.13
    def test_repr(self):
        token = NoNoTokens(jti='testjti')
        self.assertEqual(token.__repr__(), '<Token testjti>')

    # U-6.14
    def test_add(self):
        token = NoNoTokens()
        token.add()
        db_session_mock.add.assert_called_with(token)
        db_session_mock.commit.assert_called()

    # U-6.15
    def test_remove(self):
        token = NoNoTokens()
        token.remove()
        db_session_mock.delete.assert_called_with(token)
        db_session_mock.commit.assert_called()

class TestTaskReminderModel(unittest.TestCase):

    # U-6.16
    def test_repr(self):
        task = TaskReminder(task_description='Test task')
        self.assertEqual(task.__repr__(), '<taskReminder Test task>')

    # U-6.17
    def test_add(self):
        task = TaskReminder()
        task.add()
        db_session_mock.add.assert_called_with(task)
        db_session_mock.commit.assert_called()

    # U-6.18
    def test_remove(self):
        task = TaskReminder()
        task.remove()
        db_session_mock.delete.assert_called_with(task)
        db_session_mock.commit.assert_called()

    # U-6.19
    @patch('TaskTok.extensions.db.Model.query')
    def test_find_task_by_username(self, mock_query):
        TaskReminder.find_task_by_username('testuser')
        mock_query.filter_by.assert_called_with(owner_username='testuser')

if __name__ == '__main__':
    unittest.main()