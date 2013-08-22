
from pepcalk.absynt import ast_to_str, get_statements_from_code, expression_symbols, parse_simple_assignment
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
        
            
    def _get_symbol_graph(self, assignments):
        
        graph = Graph()
        for target, expression in assignments.iteritems():
            expr_symbols = expression_symbols(expression)
            target_node = self._get_or_add_node(graph, target)
            for expr_sym in expr_symbols:
                expr_node = self._get_or_add_node(graph, expr_sym)
                target_node.connect(expr_node)
        return graph


    def _order_assignments(self, assignments):
        """ Analyses the dependencies in the assignments and returns a list of targets
        """
        graph = self._get_symbol_graph(self._assignments)
        result = [node.id for node in graph.linearize()]
        assert len(result) == len(self._assignments), "sanity check"
        return result
        
        
    def execute(self):
        
        pass
        
        