import unittest
from app import Dispatcher

class DispatcherTests(unittest.TestCase):
    def test_empty_stop(self):
        d=Dispatcher()
        d.stop()
        self.assertTrue(d.released)
