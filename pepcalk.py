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
from pepcalk.graph import Node, Graph
from pepcalk.utils import check_class, logging_basic_config 

import logging
logger = logging.getLogger(__name__)


def get_or_add(graph, symbol):
    """ Gets the graph node for the symbol. Adds a node if it doesn't exist yet
    """
    if graph.contains(symbol):
        return graph.get(symbol)
    else:
        return graph.add(Node(symbol))
    
        
def get_symbol_graph(statements):
    
    graph = Graph()
    for stat in statements:
        lhs_symbols, rhs_symbols = assignment_symbols(stat)
        for lhs_sym in lhs_symbols:
            lhs_node = get_or_add(graph, lhs_sym)
            for rhs_sym in rhs_symbols:
                rhs_node = get_or_add(graph, rhs_sym)
                lhs_node.connect(rhs_node)
    return graph
            
                
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
        statements = get_statements_from_code(code)
        graph = get_symbol_graph(statements)
        print graph.linearize()            
        #browse(graph, obj_name="graph", show_root_node=True, show_special_methods = False)
        
    
         

if __name__ == '__main__':
    main()
