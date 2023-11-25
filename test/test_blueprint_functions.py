# Unit tests for TaskTok\functions.py

import unittest
from unittest.mock import patch, Mock
import subprocess
import socket
from TaskTok.blueprints.functions import verify_celery_worker, verify_message_broker_online  # Replace with actual import statement

class TestVerifyCeleryWorker(unittest.TestCase):
    #U-10.1.1
    @patch('subprocess.check_output')
    def test_verify_celery_worker_running(self, mock_check_output):
        mock_check_output.return_value = b'celery worker is running'
        self.assertTrue(verify_celery_worker())

    # U-10.1.2
    @patch('subprocess.check_output')
    def test_celery_worker_invalid(self, mock_check_output):
        mock_check_output.return_value = b''
        result = verify_celery_worker()
        self.assertFalse(result)

    # U-10.1.3
    @patch('subprocess.check_output')
    def test_verify_celery_worker_not_running(self, mock_check_output):
        mock_check_output.side_effect = subprocess.CalledProcessError(1, 'cmd', "error")
        self.assertFalse(verify_celery_worker())

class TestVerifyMessageBrokerOnline(unittest.TestCase):
    # U-10.2.1
    @patch('socket.create_connection')
    def test_verify_message_broker_online(self, mock_create_connection):
        mock_socket = Mock()   
        mock_create_connection.return_value = mock_socket
        self.assertTrue(verify_message_broker_online('localhost', 5672, 5))
        mock_socket.close.assert_called_once_with()

    # U-10.2.2
    @patch('socket.create_connection')
    def test_verify_message_broker_offline(self, mock_create_connection):
        mock_create_connection.side_effect = socket.error()
        self.assertFalse(verify_message_broker_online('localhost', 5672, 5))

if __name__ == '__main__':
    unittest.main()