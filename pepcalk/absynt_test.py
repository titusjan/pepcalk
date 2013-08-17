""" Tests for the absynt module.
"""

from __future__ import absolute_import
import unittest


from pepcalk.absynt import ast_to_str as a2s
from pepcalk.absynt import get_statement_from_code as gsfc
from pepcalk.absynt import expression_symbols as exprsym
from pepcalk.absynt import assignment_symbols as asgnsym


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
        
        self.assertEqual(a2s(gsfc("a = b + 1;")), "a = (b + 1)")
        self.assertEqual(a2s(gsfc("a = -b - -1")), "a = (-b - -1)")
        self.assertEqual(a2s(gsfc("a = a * 2 + 4")), "a = ((a * 2) + 4)")
        self.assertEqual(a2s(gsfc("a = a + 2 * 4")), "a = (a + (2 * 4))")
        self.assertEqual(a2s(gsfc("a = (a + 2) * 4")), "a = ((a + 2) * 4)")
        self.assertEqual(a2s(gsfc("a = a // 2 / 4")), "a = ((a // 2) / 4)")
        self.assertEqual(a2s(gsfc("a = a % 2 ** 4")), "a = (a % (2 ** 4))")
        self.assertNotEqual(a2s(gsfc("a = 3.33000")), "a = 3.3300") # fails. a = 3.33
        
        self.assertEqual(a2s(gsfc("a = symbol")), "a = symbol")
        self.assertEqual(a2s(gsfc("a = 'string'")), "a = 'string'")
        self.assertEqual(a2s(gsfc(r"a = 'escaped \" quote'")), "a = 'escaped \" quote'")

        # Unsupported functionality
        self.assertRaises(ValueError, a2s, gsfc("a = b = 7"))
        self.assertRaises(ValueError, a2s, gsfc("a, b = (2, 3)"))
        self.assertRaises(ValueError, a2s, gsfc("a = dir()"))
        self.assertRaises(ValueError, a2s, gsfc("a = True and False"))
        
        
    def test_expression_symbols(self):
        
        self.assertEqual(exprsym(gsfc("2 + 4")), [])
        self.assertEqual(exprsym(gsfc("a + 4")), ['a'])
        self.assertEqual(exprsym(gsfc("a + b")), ['a', 'b'])
        self.assertEqual(exprsym(gsfc("a + b + a")), ['a', 'b', 'a'])
        self.assertEqual(exprsym(gsfc("a + b * c")), ['a', 'b', 'c'])
        

    def test_assignment_symbols(self):
        
        self.assertEqual(asgnsym(gsfc("a = a + 2 / c")), (['a'], ['a', 'c']))
        self.assertEqual(asgnsym(gsfc("a = 2")), (['a'], []))
        
        # Wrong type 
        self.assertRaises(TypeError, a2s, 55)              # Not a syntax tree
        self.assertRaises(ValueError, a2s, gsfc("a == b"))      # expression
        

if __name__ == '__main__':
    unittest.main()
 