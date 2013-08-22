
import logging
from pepcalk.absynt import (ast_to_str, get_statements_from_code, wrap_expression, 
                            expression_symbols, parse_simple_assignment)
from pepcalk.graph import Node, Graph

logger = logging.getLogger(__name__)

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
        global_vars = {}
        local_vars = {}
        for name in self._order:
            expr = self._assignments[name]
            logger.debug("compiling: {} = {}".format(name, ast_to_str(expr)))
            compiled_expr = compile(wrap_expression(expr), "<string>", "eval")
            local_vars[name] = eval(compiled_expr, global_vars, local_vars)

        return local_vars
        
def main():
    import ast
    from objbrowser import browse
    
    my_expr = ast.parse("6+7", "<string>", "eval")
    
    #browse(my_expr, obj_name = 'my_expr', show_root_node = True, show_special_methods = False)
    
    source_code = "6 + 12"
    statements = get_statements_from_code(source_code)
    expression = ast.Expression()
    expression.body = statements[0].value
    #browse(locals(), show_special_methods = False)
    
    compiled_expression = compile(expression, '<string>', mode="eval")
    #browse(statements, obj_name = 'statements', show_root_node = True, show_special_methods = False)
    #print ast_to_str(expr)
    print eval(compiled_expression)
 
if __name__ == '__main__':
    main()
