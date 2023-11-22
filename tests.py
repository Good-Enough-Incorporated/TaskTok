import unittest
import tests
import os
import shutil

test_suite = unittest.TestLoader().discover('test', pattern='test*')
unittest.TextTestRunner(verbosity=2).run(test_suite)