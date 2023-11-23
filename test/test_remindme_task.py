# Unit tests for TaskTok\blueprints\views.py

import unittest

class TestTask(unittest.TestCase):
    #function from task.py
    def add(self, x, y):
        return x + y

    # U-3.3
    def test_add(self):
        self.assertEqual(self.add(3, 5), 8)
        self.assertEqual(self.add(-1, 4), 3)
        self.assertEqual(self.add(-1, -2), -3)
        self.assertEqual(self.add(0, 0), 0)

if __name__ == '__main__':
    unittest.main()