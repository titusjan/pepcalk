""" pepcalk module

TODO: booleans, complex numbers.

Applications:
    - Btw bonnetjes.
    - Compact calendar
    - Signal processing
    - Dagobert
    - Measurement database

"""

from astviewer import view
from objbrowser import browse

from pepcalk.absynt import get_statements_from_code, assignment_symbols
from pepcalk.calculation import Calculation
from pepcalk.utils import check_class, logging_basic_config 

import logging
logger = logging.getLogger(__name__)



            
      
def main():
    logging_basic_config("DEBUG")
    
    if 0:
        correct_code = ["b = -2 -(-a) + (+a2)", 
                        #"e, f = range(2)",
                        "l = [1,2,3]",  
                        "a = True; a2 = '5'" , 
                        "l[1] = 9",
                        "c = a+3", 
                        "d = c * b", 
                        "arr = np.array([234, 25])"]
        self_ref_code = ["a = 6", "b = -2", "a=a+2"]
        code = "\n".join(correct_code)
    else:
        code = """
b = 2*a
a = 5
c = b+a
        """
    
    
    if 0:
        view(source_code = "a+b", mode="single", width=800, height=600)
    else:
        calc = Calculation(code)
        print calc.get_source_code()
        print ""
        result = calc.execute()
        for name, value in sorted(result.iteritems()):
            print "{} = {}".format(name, value)
        
        
        #browse(graph, obj_name="graph", show_root_node=True, show_special_methods = False)
        
    
         

if __name__ == '__main__':
    main()
