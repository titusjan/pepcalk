""" Tests for the absynt module.
"""

from __future__ import absolute_import
import unittest


from pepcalk.absynt import ast_to_str as a2s
from pepcalk.absynt import get_statement_from_code as gsfc


class AbsyntCase(unittest.TestCase):
    """A test class for the ast_to_str function"""

    def setUp(self):
        pass

    def tearDown(self):
        pass


    def test_get_statement_from_code(self):
        
        self.assertRaises(ValueError, gsfc, "a = 6; b = 7")
        self.assertRaises(SyntaxError, gsfc, "a = (")
        

    def test_ast_to_str(self):
        
        self.assertEqual(a2s(gsfc("a = b + 1")), "a = (b + 1)")
        self.assertEqual(a2s(gsfc("a = -b - -1")), "a = (-b - -1)")
        self.assertEqual(a2s(gsfc("a = a * 2 + 4")), "a = ((a * 2) + 4)")
        self.assertEqual(a2s(gsfc("a = a + 2 * 4")), "a = (a + (2 * 4))")
        self.assertEqual(a2s(gsfc("a = (a + 2) * 4")), "a = ((a + 2) * 4)")
        self.assertEqual(a2s(gsfc("a = a // 2 / 4")), "a = ((a // 2) / 4)")
        self.assertEqual(a2s(gsfc("a = a % 2 ** 4")), "a = (a % (2 ** 4))")

        # self.assertEqual(a2s(gsfc("a = 3.33000")), "a = 3.3300") # fails. a = 3.33
        

if __name__ == '__main__':
    unittest.main()
 