""" Tests for the absynt module.
"""

from __future__ import absolute_import
import unittest

from pepcalk.absynt import CompilationError
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
        
        self.assertRaises(CompilationError, gsfc, "a = 6; b = 7")
        self.assertRaises(SyntaxError, gsfc, "a = (")
        

    def test_ast_to_str(self):
        
        self.assertEqual(a2s(gsfc("a = b + 1;")), "a = (b + 1)")
        self.assertEqual(a2s(gsfc("a = +b - -1")), "a = (+b - -1)")
        self.assertEqual(a2s(gsfc("a = -b - -1")), "a = (-b - -1)")
        self.assertEqual(a2s(gsfc("a = a * 2 + 4")), "a = ((a * 2) + 4)")
        self.assertEqual(a2s(gsfc("a = a + 2 * 4")), "a = (a + (2 * 4))")
        self.assertEqual(a2s(gsfc("a = (a + 2) * 4")), "a = ((a + 2) * 4)")
        self.assertEqual(a2s(gsfc("a = a // 2 / 4")), "a = ((a // 2) / 4)")
        self.assertEqual(a2s(gsfc("a = a % 2 ** 4")), "a = (a % (2 ** 4))")
        self.assertNotEqual(a2s(gsfc("a = 3.33000")), "a = 3.3300") # fails. a = 3.33
        
        # Other types
        self.assertEqual(a2s(gsfc("a = symbol")), "a = symbol")
        self.assertEqual(a2s(gsfc("a = 'string'")), "a = 'string'")
        self.assertEqual(a2s(gsfc(r"a = 'escaped \" quote'")), "a = 'escaped \" quote'")
        
        # None is just a symbol within an AST
        self.assertEqual(a2s(gsfc("a = None + 1;")), "a = (None + 1)")
        
        self.assertEqual(a2s(gsfc("a = True and False and True")), "a = (True and False and True)")
        self.assertEqual(a2s(gsfc("a = True or False or 3")), "a = (True or False or 3)")
        self.assertEqual(a2s(gsfc("a = True or False and True")), "a = (True or (False and True))")
        
        self.assertEqual(a2s(gsfc("a = b1.c1.c2")), "a = b1.c1.c2")
        
        # Function calls
        self.assertEqual(a2s(gsfc("a = dir()")), "a = dir()")
        self.assertEqual(a2s(gsfc("a = my_fun(a, b)")), "a = my_fun(a, b)")
        self.assertEqual(a2s(gsfc("a = my_fun(7, None)")), "a = my_fun(7, None)")
        self.assertEqual(a2s(gsfc("a = my_fun(b = 3, a=22)")), "a = my_fun(b=3, a=22)")
        self.assertEqual(a2s(gsfc("a = my_fun(-12, s='after')")), "a = my_fun(-12, s='after')")
        self.assertEqual(a2s(gsfc("a = f(g('nested call'))")), "a = f(g('nested call'))")
        
        # non-keyword arg after keyword arg
        self.assertRaises(SyntaxError, gsfc, "a = my_fun(s='before', -12)")
        
        # Unsupported functionality
        self.assertRaises(CompilationError, a2s, gsfc("a = my_fun(6, *args)"))
        self.assertRaises(CompilationError, a2s, gsfc("a = my_fun(6, **kwargs)"))
        self.assertRaises(CompilationError, a2s, gsfc("a = b = 7"))
        self.assertRaises(CompilationError, a2s, gsfc("a, b = (2, 3)"))
        #self.assertRaises(CompilationError, a2s, gsfc("a = dir()"))
        
        
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
        self.assertRaises(CompilationError, a2s, gsfc("a == b"))      # expression
        

if __name__ == '__main__':
    unittest.main()
