""" pepcalk module

TODO: booleans, complex numbers.

Applications:
    - Btw bonnetjes.
    - Compact calendar
    - Signal processing
    - Dagobert
    - Measurement database

"""

import ast
import numpy as np
from astviewer import view
from objbrowser import browse

from pepcalk.utils import check_class, logging_basic_config 
from pepcalk.absynt import get_statements_from_code

import logging
logger = logging.getLogger(__name__)

    
    
def main():
    logging_basic_config("DEBUG")
    
    correct_code = ["a = True; a2 = '5'" , 
                    "b = -2 -(-a) + (+a2)", 
                    "c = a+3", 
                    "d = c * b", 
                    #"e, f = range(2)",
                    "l = [1,2,3]",  
                    "l[1] = 9",
                    "arr = np.array([234, 25])"]
    self_ref_code = ["a = 6", "b = -2", "a=a+2"]
    code = "\n".join(correct_code)
    
    if 0:
        view(source_code = "a+b", mode="single", width=800, height=600)
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
