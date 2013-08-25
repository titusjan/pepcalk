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
        
        # Support for from __future__ import division
        result = Calculation("a = 5/2" ).compile().execute()
        self.assertEqual(result['a'], 2.5)
         
        
        # Undefined variable
        calc = Calculation("b = a * 2; a = c" ).compile()
        self.assertRaises(NameError, calc.execute) # TODO: other Error?
        
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
        
        # Boolean
        result = Calculation("b = True; a = not b; c = b or a" ).compile().execute()
        self.assertEqual(result['a'], False)
        self.assertEqual(result['b'], True)
        self.assertEqual(result['c'], True)
        
        # NoneTypes
        result = Calculation("b = None" ).compile().execute()
        self.assertEqual(result['b'], None)
        
        # Function calls
        result = Calculation("b = int(5.4)" ).compile().execute()
        self.assertEqual(result['b'], 5)
        
        result = Calculation("b = int('10', base=2)" ).compile().execute()
        self.assertEqual(result['b'], 2)

        
if __name__ == '__main__':
    unittest.main()
