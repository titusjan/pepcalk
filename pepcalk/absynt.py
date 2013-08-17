""" Abstract Syntax Tree (AST) module

    Only a very limited subset of Python ASTs are supported.
    
    TODO: boolean. Complex?
"""
from __future__ import absolute_import, division

import ast
from pepcalk.utils import check_class


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
        raise ValueError("Body should consist of one statement. Got: {}".
                         format(len(module.body)))
    return module.body[0]


def ast_to_str(node):
    """ String representation of an abstract syntax tree
    """
    node_type = type(node)
    
    if node_type == ast.Num:
        return str(node.n)
    elif node_type == ast.Str:
        return node.s
    elif node_type == ast.Name:
        return node.id
    
    elif node_type == ast.UnaryOp:
        return ast_to_str(node.op) + ast_to_str(node.operand)
    elif node_type == ast.USub:
        return "-"
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
    
    elif node_type == ast.Assign:
        # Targets can have more than one element. E.g. when the statement is: a = b = 6
        # This is not supported (at the moment)
        if len(node.targets) != 1:
            raise ValueError("Targets should be of length 1. Got: {}".format(len(node.targets)))
        
        target = node.targets[0]
        if not isinstance(target.ctx, ast.Store):
            raise AssertionError("Target.ctx should be store. Got: {}".format(target.ctx))
        
        return "{} = {}".format(target.id, ast_to_str(node.value))
    
    else:
        return TypeError("Unsupported node type: {}".format(node_type))
    
    
if __name__ == "__main__":
    
    print ast_to_str(get_statement_from_code("a = 3.33000"))
    
        