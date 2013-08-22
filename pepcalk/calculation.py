
from pepcalk.absynt import ast_to_str, get_statements_from_code, assignment_symbols, parse_simple_assignment
from pepcalk.graph import Node, Graph

class Calculation(object):

    def __init__(self, code = ""):
        "constructor"
        self._code = code
        self._assignments = dict()
        self._order = []
        self.init_from_code(code)
    
        
    @property        
    def assignments(self):
        return self._assignments
    
            
    def init_from_code(self, code):
        """ Sets the code of the
        """
        self._code = code
        for stat in get_statements_from_code(code):
            lhs_symbol, expression = parse_simple_assignment(stat)
            self._assignments[lhs_symbol.id] = expression
    
        self._order = self._order_assignments(self._assignments)
        
        
    def export_to_code(self):
        """ Writes the assignments as a code string with one expression per line.
        """
        strings = []
        for name in self._order:
            strings.append("{} = {}".format(name, ast_to_str(self.assignments[name])))
        return "\n".join(strings)
    
        
    def _get_or_add_node(self, graph, symbol):
        """ Gets the graph node for the symbol. Adds a node if it doesn't exist yet
        """
        if graph.contains(symbol):
            return graph.get(symbol)
        else:
            return graph.add(Node(symbol))
        
            
    def _get_symbol_graph(self, statements):
        
        graph = Graph()
        for stat in statements:
            lhs_symbols, rhs_symbols = assignment_symbols(stat)
            for lhs_sym in lhs_symbols:
                lhs_node = self._get_or_add_node(graph, lhs_sym)
                for rhs_sym in rhs_symbols:
                    rhs_node = self._get_or_add_node(graph, rhs_sym)
                    lhs_node.connect(rhs_node)
        return graph


    def _order_assignments(self, assignments):
        """ Analyses the dependencies in the assignments and returns a list of targets
        """
        statements = get_statements_from_code(self._code) # TODO
        graph = self._get_symbol_graph(statements)
        result = [node.id for node in graph.linearize()]
        assert len(result) == len(statements), "sanity check"
        return result
        
        
    def execute(self):
        
        pass
        
        