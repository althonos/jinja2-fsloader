import sys
import unittest

from jinja2_fsloader import to_unicode


class TestMisc(unittest.TestCase):
    def test_to_unicode(self):
        expected = to_unicode("abc")
        if sys.version_info[0] == 2:
            self.assertTrue(isinstance(expected, unicode))
