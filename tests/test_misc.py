import unittest

from jinja2_fsloader import to_unicode, PY2


class TestMisc(unittest.TestCase):
    def test_to_unicode(self):
        expected = to_unicode("abc")
        if PY2:
            self.assertTrue(isinstance(expected, unicode))
