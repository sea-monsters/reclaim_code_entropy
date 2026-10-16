import unittest
from parcel import render

class ParcelTest(unittest.TestCase):
    def test_render(self):
        self.assertEqual(render(" Straße ", permitted=True), "strasse")
    def test_denied(self):
        with self.assertRaises(PermissionError):
            render(None)
