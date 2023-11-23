# Unit tests for RemindMeClient\celeryManager.py

import unittest
from unittest.mock import patch, MagicMock
from flask import Flask
from celery import Celery, Task
from RemindMeClient.celeryManager import celery_init_app


class TestCeleryManager(unittest.TestCase):
    def setUp(self):
        self.flask_app = Flask(__name__)
        self.flask_app.config['CELERY'] = {
            'broker_url': 'memory://',
            'result_backend': 'cache',
            'cache_backend': 'memory'
        }

    # U-2.1
    @patch('flask.Flask.app_context')
    def test_celery_init_app(self, app_context_mock):
        app_context_mock.return_value = MagicMock()
        celery_app = celery_init_app(self.flask_app)
        FlaskTask = celery_app.Task

        self.assertIsInstance(celery_app, Celery)
        self.assertEqual(celery_app.conf['broker_url'], self.flask_app.config['CELERY']['broker_url'])
        self.assertEqual(celery_app.conf['result_backend'], self.flask_app.config['CELERY']['result_backend'])
        self.assertEqual(celery_app.main, self.flask_app.name)
        self.assertIs(celery_app.Task, FlaskTask)
        self.assertIn('celery', self.flask_app.extensions)
        self.assertIs(self.flask_app.extensions['celery'], celery_app)

if __name__ == '__main__':
    unittest.main()