import sys
import unittest

from jinja2_fsloader import _to_unicode


class TestMisc(unittest.TestCase):
    def test_to_unicode(self):
        expected = _to_unicode("abc")
        if sys.version_info[0] == 2:
            self.assertIsInstance(expected, unicode)
        else:
            self.assertIsInstance(expected, str)
