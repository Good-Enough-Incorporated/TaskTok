# Unit tests for TaskTok\functions.py

import unittest
from unittest.mock import patch, Mock
import subprocess
import socket
from itsdangerous import URLSafeTimedSerializer
from TaskTok.functions import verifyCeleryWorker, verifyMessageBrokerOnline, generate_email_token, verify_email_token

os_mock = Mock()
os_mock.environ = {
    'EMAIL_VERIFICATION_SECRET': 'secret-key',
    'SECURITY_PASSWORD_SALT': 'salt'
}

class TestSystemChecks(unittest.TestCase):

    # U-5.1.1
    @patch('subprocess.check_output')
    def test_verify_celery_worker_running(self, mock_check_output):
        mock_check_output.return_value = b'celery worker is running'
        self.assertTrue(verifyCeleryWorker())

    # U-5.1.2
    @patch('subprocess.check_output')
    def test_celery_worker_invalid(self, mock_check_output):
        mock_check_output.return_value = b''
        result = verifyCeleryWorker()
        self.assertFalse(result)

    # U-5.1.3
    @patch('subprocess.check_output')
    def test_verify_celery_worker_not_running(self, mock_check_output):
        mock_check_output.side_effect = Exception('error')
        self.assertFalse(verifyCeleryWorker())

    # U-5.2.1
    @patch('socket.create_connection')
    def test_verify_message_broker_online(self, mock_create_connection):
        mock_socket = Mock()   
        mock_create_connection.return_value = mock_socket
        self.assertTrue(verifyMessageBrokerOnline('localhost', 5672, 5))
        mock_socket.close.assert_called_once_with()

    # U-5.2.2
    @patch('socket.create_connection')
    def test_verify_message_broker_offline(self, mock_socket):
        mock_socket.side_effect = socket.error
        self.assertFalse(verifyMessageBrokerOnline('localhost', 5672, 5))

    # U-5.3
    @patch.dict('os.environ', {'EMAIL_VERIFICATION_SECRET': 'secret-key', 'SECURITY_PASSWORD_SALT': 'salt'})
    def test_generate_email_token(self):
        email = 'user@tasktok.com'
        token = generate_email_token(email)
        self.assertIsNotNone(token)

    # U-5.4.1
    @patch.dict('os.environ', {'EMAIL_VERIFICATION_SECRET': 'secret-key', 'SECURITY_PASSWORD_SALT': 'salt'})
    def test_verify_email_token(self):
        email = 'user@tasktok.com'
        token = generate_email_token(email)
        verified_email = verify_email_token(token)
        self.assertEqual(verified_email, email)

    # U-5.4.2
    @patch.dict('os.environ', {'EMAIL_VERIFICATION_SECRET': 'secret-key', 'SECURITY_PASSWORD_SALT': 'salt'})
    def test_verify_email_token_invalid(self):
        token = 'invalid-token'
        verified_email = verify_email_token(token)
        self.assertFalse(verified_email)

if __name__ == '__main__':
    unittest.main()