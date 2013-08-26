""" Abstract Syntax Tree (AST) module

    Only a very limited subset of Python ASTs are supported.
    
    TODO: boolean. Complex?
"""
from __future__ import absolute_import, division

import ast
from pepcalk.utils import check_class


class CompilationError(StandardError):
    """ Raised when the calculation cannot be compiled."""
    pass


def get_statements_from_code(code):
    """ Compiles the code string in 'exec' mode.
        Verifies it consists of a list of statements and returns this list.
    """
    module = ast.parse(code, mode="exec")
    check_class(module, ast.Module)
    return module.body

    
def get_statement_from_code(code):
    """ Compiles the code string in 'single' mode
        Verifies it consists of a list of one statement element and returns this list.
    """
    module = ast.parse(code, mode="single")
    check_class(module, ast.Interactive)
    # In single mode the body can still consist of multiple statements
    # if they are separated by a semicolon. We don't support this.
    if len(module.body) != 1:
        raise CompilationError("Body should consist of one statement. Got: {}".
                               format(len(module.body)))
    return module.body[0]


def ast_to_str(node):
    """ String representation of an abstract syntax tree
    """
    check_class(node, ast.AST)
    node_type = type(node)
    
    if node_type == ast.Num:
        return repr(node.n)  # escapes quotes
    elif node_type == ast.Str:
        return repr(node.s)
    elif node_type == ast.Name:
        return node.id
    
    elif node_type == ast.UnaryOp:
        return ast_to_str(node.op) + ast_to_str(node.operand)
    elif node_type == ast.Not:
        return "not "
    elif node_type == ast.UAdd:
        return "+"
    elif node_type == ast.USub:
        return "-"
    
    elif node_type == ast.BinOp:
        return "({} {} {})".format(ast_to_str(node.left), 
                                   ast_to_str(node.op), 
                                   ast_to_str(node.right))
    elif node_type == ast.Add:
        return "+"
    elif node_type == ast.Sub:
        return "-"
    elif node_type == ast.Mult:
        return "*"
    elif node_type == ast.Div:
        return "/"
    elif node_type == ast.FloorDiv:
        return "//"
    elif node_type == ast.Mod:
        return "%"
    elif node_type == ast.Pow:
        return "**"
    
    elif node_type == ast.BoolOp:
        op_str = " {} ".format(ast_to_str(node.op))
        return '(' + op_str.join([ast_to_str(val) for val in node.values]) + ')'
    elif node_type == ast.And:
        return "and"    
    elif node_type == ast.Or:
        return "or"
    
    elif node_type == ast.Attribute:
        if not isinstance(node.ctx, ast.Load):
            raise CompilationError("Only Attribute node.ctx 'Load' supported. Got: {}"
                                   .format(node.ctx))    
        return "{}.{}".format(ast_to_str(node.value), node.attr)
    
    elif node_type == ast.Call:
        
        # Check for unsupported functionality: *args, **kwargs 
        if node.starargs is not None:
            raise CompilationError("*args not supported.")
        if node.kwargs is not None:
            raise CompilationError("**kwargs not supported.")
        
        # Check for unsupported functionality: functions be a named function
        if not isinstance(node.func, (ast.Name, ast.Attribute)):
            raise CompilationError("node.func should be a Name node. Got: {}"
                                   .format(node.func))

        if not isinstance(node.func.ctx, ast.Load): # sanity check 
            raise AssertionError("node.func.ctx should be store. Got: {}".format(node.func.ctx))
        
        param_strings = []
        for arg in node.args:
            #print "node.arg: {!r}: (id={}) {}".format(arg, arg.id, ast_to_str(arg))
            param_strings.append(ast_to_str(arg))
        for keyword in node.keywords:
            param_strings.append(ast_to_str(keyword))
        #print param_strings
        return "{}({})".format(ast_to_str(node.func), ', '.join(param_strings))

    elif node_type == ast.keyword:
        check_class(node.arg, basestring)
        return "{}={}".format(node.arg, ast_to_str(node.value))
    
    elif node_type == ast.Assign:
        # Targets can have more than one element. E.g. when the statement is: a = b = 6
        # This is not supported (at the moment)
        if len(node.targets) != 1:
            raise CompilationError("Targets should be of length 1. Got: {}"
                                   .format(len(node.targets)))
        target = node.targets[0]
        if not isinstance(target, ast.Name):
            raise CompilationError("Target should be a Name node. Got: {}"
                                   .format(target))
        
        if not isinstance(target.ctx, ast.Store): # sanity check 
            raise AssertionError("Target.ctx should be store. Got: {}".format(target.ctx))
        
        return "{} = {}".format(target.id, ast_to_str(node.value))
    
    else:
        raise CompilationError("Unsupported node type: {}".format(node_type))
    

def wrap_expression(expr):
    """ Wraps an ast.expr node into an ast.Expression node, which can be used by compile()
    """
    check_class(expr, ast.expr)
    expression = ast.Expression()
    expression.body = expr
    return expression    
    

# TODO: use symbtable module?
def expression_symbols(node):
    """ Returns a list of symbols used in an expression.
    
        Does not check for unsupported functionality; use ast_to_st for that.
    """
    check_class(node, ast.AST)
    node_type = type(node)
    
    if node_type == ast.Expr:
        return expression_symbols(node.value)
    elif node_type == ast.Num:
        return []
    elif node_type == ast.Str:
        return []
    elif node_type == ast.Name:
        return [node.id]
    elif node_type == ast.UnaryOp:
        return expression_symbols(node.operand)
    elif node_type == ast.BinOp:
        return expression_symbols(node.left) + expression_symbols(node.right)
    elif node_type == ast.BoolOp:
        result = []
        for val in node.values:
            result += expression_symbols(val)
        return result
    elif node_type == ast.Attribute:
        return expression_symbols(node.value)
    elif node_type == ast.Call:
        result = []
        for arg in node.args:
            result += expression_symbols(arg)
        for keyword in node.keywords:
            result += expression_symbols(keyword)
        return result
    elif node_type == ast.keyword:
        return expression_symbols(node.value)
    else:
        raise CompilationError("Unsupported node type: {}. Statement: {}"
                               .format(node_type, ast.dump(node)))
    

def assignment_symbols(node):
    """ Returns (lsymbols, rsymbols) tuple, where lsymbols and rsymbols are the lists of
        symbols used left and right of the assignment operator.
    """
    lhs_name, expression = parse_simple_assignment(node)
    return expression_symbols(lhs_name), expression_symbols(expression)


def parse_simple_assignment(node):
    """ Returns (lhs_name, expression) tuple.
    
        Raises a CompilationError if the node is not an assignment that assigns to a 
        single variable.
    """
    check_class(node, ast.AST)
    node_type = type(node)
    
    if node_type == ast.Assign:
        # Targets can have more than one element. E.g. when the statement is: a = b = 6
        # This is not supported (at the moment)
        if len(node.targets) != 1:
            raise CompilationError("Targets should be of length 1. Got: {}"
                                   .format(len(node.targets)))
        
        target = node.targets[0]
        if not isinstance(target.ctx, ast.Store): # sanity check
            raise AssertionError("Target.ctx should be store. Got: {}".format(target.ctx))
        
        return (target, node.value)
    else:
        raise CompilationError("Unsupported node type: {}".format(node_type))
        
    
if __name__ == "__main__":
    
    from astviewer import view
    
    def main():
        #stat = get_statement_from_code("b = True")
        view(source_code = "b = my_fun( a= None)")

if __name__ == "__main__":
    main()    