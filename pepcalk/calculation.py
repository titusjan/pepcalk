
import logging
from pepcalk.absynt import (CompilationError, ast_to_str, 
                            get_statements_from_code, wrap_expression, 
                            expression_symbols, parse_simple_assignment)
from pepcalk.graph import Node, Graph

logger = logging.getLogger(__name__)



class Calculation(object):

    def __init__(self, code = ""):
        "constructor"
        self._code = code
        self._assignments = dict()
        self._compiled = None # list of (target, compiled_expr) tuples.
        self.import_from_source_code(code)
    
        
    @property        
    def assignments(self):
        return self._assignments
    
            
    def import_from_source_code(self, code):
        """ Sets the code of the
        """
        self._code = code
        for stat in get_statements_from_code(code):
            lhs_symbol, expression = parse_simple_assignment(stat)
            target = lhs_symbol.id
            if target not in self._assignments:
                self._assignments[target] = expression
            else:
                raise CompilationError("Duplicate target symbol found: {}".format(target))

    
        
    def export_source_code(self):
        """ Compiles the assignments if necessary and returns it as Python statements.
        """
        if not self.is_compiled:
            self.compile()
            
        strings = []
        for target, _ in self._compiled:
            strings.append("{} = {}".format(target, ast_to_str(self.assignments[target])))
        return "\n".join(strings)

        
            
    def _get_symbol_graph(self, assignments):
        """ Create a graph with the dependencies of all symbols
        """
        def get_or_add_node(graph, symbol):
            """ Gets the graph node for the symbol. Adds a node if it doesn't exist yet
            """
            if graph.contains(symbol):
                return graph.get(symbol)
            else:
                return graph.add(Node(symbol))
            
        graph = Graph()
        for target, expression in assignments.iteritems():
            expr_symbols = expression_symbols(expression)
            target_node = get_or_add_node(graph, target)
            for expr_sym in expr_symbols:
                expr_node = get_or_add_node(graph, expr_sym)
                target_node.connect(expr_node)
        return graph


    def _order_assignments(self, assignments):
        """ Analyses the dependencies in the assignments and returns a list of targets
        """
            
        graph = self._get_symbol_graph(self._assignments)
        try:
            ordered_nodes = graph.linearize()
        except ValueError, ex: # circular dependency
            raise CompilationError(ex.message)
        
        result = [node.id for node in ordered_nodes]

        all_symbols = set(result)
        target_symbols = set(assignments.iterkeys())
        if not target_symbols == all_symbols:
            raise CompilationError("Undefined symbol(s): {}".
                                   format(", ".join(all_symbols - target_symbols)))
        return result
    
    
    @property
    def is_compiled(self):
        " Returns True if the assignments are compiled."
        return self._compiled is not None
    
    
    def compile(self):
        """ Compiles and orders the assignments
        """
        self._compiled = []
        for target in self._order_assignments(self._assignments):
            expr = self._assignments[target]
            #logger.debug("compiling: {} = {}".format(name, ast_to_str(expr)))
            compiled_expr = compile(wrap_expression(expr), "<string>", "eval")
            self._compiled.append( (target, compiled_expr) )
            
        
    def execute(self):
        """ Executes the asssignments. Returns dictionary with results
        """
        if not self.is_compiled:
            self.compile()
            
        global_vars = {}
        local_vars = {}
        for target, compiled_expr in self._compiled:
            local_vars[target] = eval(compiled_expr, global_vars, local_vars)

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
