""" pepcalk module

TODO: booleans, complex numbers.

"""

import ast
import numpy as np
from astviewer import view
from objbrowser import browse

from pepcalk.utils import check_class, logging_basic_config 
from pepcal.absynt import get_statements_from_code

import logging
logger = logging.getLogger(__name__)

    
def parse_assign_statement(statement):
    """ Parses an assign statement and returns tuple of inputs and a tuple of outputs
    """
    check_class(statement, ast.Assign)

    # Targets can have more than one element. E.g. when the statement is: a = b = 6
    # This is not supported (at the moment)
    if len(statement.targets) != 1:
        raise ValueError("Targets should be of length 1. Got: {}".format(len(statement.targets)))
    
    target = statement.targets[0]
    if not isinstance(target.ctx, ast.Store):
        raise ValueError("Target.ctx should be store. Got: {}".format(target.ctx))
    
    return target.id

    
    
def main():
    logging_basic_config("DEBUG")
    
    correct_code = ["a = 6; a2 = '5'" , 
                    "b = -2 -(-a) + (+a2)", 
                    "c = a+3", 
                    "d = c * b", 
                    #"e, f = range(2)",
                    "l = [1,2,3]",  
                    "l[1] = 9",
                    "arr = np.array([234, 25])"]
    self_ref_code = ["a = 6", "b = -2", "a=a+2"]
    code = "\n".join(correct_code)
    
    if 1:
        view(source_code = code, mode="single", width=800, height=600)
    else:
        statements = get_statements_from_code(code)
            
        inputs = []
        for stat in statements:
            logger.debug("Parsing: {}".format(ast.dump(stat)))
            try:
                inputs.append(parse_assign_statement(stat))
            except StandardError, ex:
                logger.exception(ex)
                view(source_code = code, mode="exec", width=800, height=600)
                raise
    
        print inputs
    
         

if __name__ == '__main__':
    main()
