
import logging, ast
from pepcalk.absynt import (CompilationError, ast_to_str, wrap_expression, 
                            get_statement_from_code, get_statements_from_code, 
                            expression_symbols, parse_simple_assignment)
from pepcalk.graph import Node, Graph

logger = logging.getLogger(__name__)


def assignment_order(assignment):
    return assignment.order



class Assignment(object):
    """ The assignments in the calculation
    """
    def __init__(self, init = None, order = None):
        
        self._target = None
        self._expression = None
        self._compiled_expr = None
        self._value = None
        self._order = order
        
        if init is None:
            assert False, "not yet decided on implementation"
        elif isinstance(init, ast.AST):
            self.init_from_ast(init)
        else:
            self.init_from_code(init)
        
    def __str__(self):
        return "{} = {}".format(self._target, self.source)
    
    @property        
    def target(self):
        return self._target
    
    @property       
    def source(self):
        return ast_to_str(self._expression)

    @property       
    def expression(self):
        return self._expression
    
    @property
    def compiled_expression(self):
        return self._compiled_expr
    
    @property       
    def order(self):
        return self._order
    
    @order.setter       
    def order(self, val):
        self._order = val
    
    @property
    def order_str(self):
        " The order as a string "
        if self.order is None:
            return ""
        else:
            return "{:2d}".format(self.order)
        
    @property       
    def value(self):
        "The value after execution."
        return self._value
    
    @value.setter       
    def value(self, val):
        "The value after execution."
        self._value = val


    def reset(self):
        """ Sets order, value and compiled_expr to None
        """
        self.order = None
        self._compiled_expr = None
        self.value = None
        

    def init_from_code(self, code_line):
        """ Initialize an assignment from a string in the form of: target = source
        """
        statement_node = get_statement_from_code(code_line)
        self.init_from_ast(statement_node)
        
    
    def init_from_ast(self, statement_node):
        """ Initialize an assignment from an ast.Assign object
        """
        lhs_symbol, expr = parse_simple_assignment(statement_node)
        self.reset()
        self._expression = expr
        self._target = lhs_symbol.id


    def compile(self):
        """ Compiles the expression
        """
        self._compiled_expr = compile(wrap_expression(self.expression), 
                                      "<string>", "eval")


class Calculation(object):

    def __init__(self, code = ""):
        "Constructor"
        self._assignments = []
        self.import_from_source_code(code)

    def __len__(self):
        "Number of assignment in the calculation"
        return len(self._assignments)
        
    @property        
    def assignments(self):
        return self._assignments
    
    
    def reset(self):
        """ Resets all assignments
        """
        for assignment in self.assignments:
            assignment.reset()
            
            
    def summary(self):
        """ Returns a multiline summary string
        """
        strings = []
        for asgn in self._assignments:
            strings.append("{}: value = {:5}; {} "
                           .format(asgn.order_str, asgn.value, str(asgn), ))
        return "\n".join(strings)
    
            
    def import_from_source_code(self, code):
        """ Sets the code of the
        """
        self._assignments = []
        for stat in get_statements_from_code(code):
            self._assignments.append(Assignment(stat))
    
        
    def export_to_source_code(self):
        """ Compiles the assignments if necessary and returns it as Python statements.
        """
        return '\n'.join([str(assign) for assign in self.assignments])

            
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
        for assignment in assignments:
            expr_symbols = expression_symbols(assignment.expression)
            target_node = get_or_add_node(graph, assignment.target)
            for expr_sym in expr_symbols:
                expr_node = get_or_add_node(graph, expr_sym)
                target_node.connect(expr_node)
        return graph


    def _sort_assignments(self):
        """ Analyses the dependencies in the assignments and returns a list of targets
        """
        # Create assignment index by target
        assignment_dict = dict()
        for assignment in self.assignments:
            if assignment.target not in assignment_dict: # TODO: ordered dict?
                assignment_dict[assignment.target] = assignment
            else:
                raise CompilationError("Duplicate target symbol found: {}"
                                       .format(assignment.target))

        graph = self._get_symbol_graph(self._assignments)
        try:
            ordered_nodes = graph.linearize()
        except ValueError, ex: # circular dependency
            raise CompilationError(ex.message)
        
        lhs_symbols = [node.id for node in ordered_nodes]

        all_symbols = set(lhs_symbols)
        target_symbols = set([assign.target for assign in self.assignments])
        if not target_symbols == all_symbols:
            raise CompilationError("Undefined symbol(s): {}".
                                   format(", ".join(all_symbols - target_symbols)))
            
        for order, lhs_sym in enumerate(lhs_symbols):
            assignment_dict[lhs_sym].order = order

    
    def compile(self):
        """ Compiles and orders the assignments.
        
            Returns self so that you can use it in a chain: calc.compile().execute()
        """
        self.reset()
        self._sort_assignments()
        for assignment in self.assignments:
            assignment.compile()
        return self
            
        
    def execute(self):
        """ Executes the assignments. Returns dictionary with results.
        
            Pre: the calculation must be compiled first.
        """
        for assignment in self.assignments:
            if assignment.compiled_expression is None:
                raise AssertionError("Pre: assignment is not compiled: {}".format(assignment))
            
        global_vars = {}
        local_vars = {}
        for assignment in sorted(self.assignments, key=assignment_order):
            assignment.value = eval(assignment.compiled_expression, global_vars, local_vars)
            local_vars[assignment.target] = assignment.value
            
        return local_vars
        
        
    def sort(self, key, reverse=False):
        """ Sorts the order of the calculation as they are stored.
        
            Note: doesn't change the order field, which is used to determine the
            execution order.
        """
        self._assignments.sort(key = key, reverse = reverse)
        
         