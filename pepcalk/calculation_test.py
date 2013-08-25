""" Tests for the absynt module.
"""

from __future__ import absolute_import
import unittest
from pepcalk.absynt import CompilationError
from pepcalk.calculation import Calculation


class Case(unittest.TestCase):
    """A test class for the ast_to_str function"""

    def setUp(self):
        pass

    def tearDown(self):
        pass


    def test_execute(self):
        
        # Empty program
        result = Calculation("").execute()
        self.assertEqual(result, {})
        
        # Regular case
        result = Calculation("b = a * 2; a = 4" ).compile().execute()
        self.assertEqual(result['a'], 4)
        self.assertEqual(result['b'], 8)
        
        # Undefined variable
        calc = Calculation("b = a * 2; a = c" )
        self.assertRaises(CompilationError, calc.compile)
        
        # Circular dependency
        calc = Calculation("a = a / 2" )
        self.assertRaises(CompilationError, calc.compile)
        
        # Non assignments
        self.assertRaises(CompilationError, Calculation, "print a" )
        self.assertRaises(CompilationError, Calculation, "6 + 4" )
        
        # Target used twice
        calc = Calculation("a = 5; a = 2")
        self.assertRaises(CompilationError, calc.compile)
        
        # Syntax error
        self.assertRaises(SyntaxError, Calculation, "a = 5ttt" )
        
        # TODO: test None  
        
        
if __name__ == '__main__':
    unittest.main()
