import unittest
from app import format_id

class FormatTests(unittest.TestCase):
    def test_formats(self):
        self.assertEqual(format_id(0), 'item-0')
        self.assertEqual(format_id('旧'), 'item-旧')
