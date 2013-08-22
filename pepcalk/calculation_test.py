""" Tests for the absynt module.
"""

from __future__ import absolute_import
import unittest



class Case(unittest.TestCase):
    """A test class for the ast_to_str function"""

    def setUp(self):
        pass

    def tearDown(self):
        pass


    def test_get_statement_from_code(self):
        
        code = """ 
b = a * 2
a = 4 
        """
        
        self.assertRaises(ValueError, gsfc, "a = 6; b = 7")
        self.assertRaises(SyntaxError, gsfc, "a = (")

if __name__ == '__main__':
    unittest.main()
 