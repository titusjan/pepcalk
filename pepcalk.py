import logging, ast
from astviewer import view
from objbrowser import browse

logger = logging.getLogger(__name__)

def logging_basic_config(level):
    """ Setup basic config logging. Useful for debugging to quickly setup a useful logger"""
    fmt = '%(filename)20s:%(lineno)-4d : %(levelname)-7s: %(message)s'
    logging.basicConfig(level=level, format=fmt)

    
def check_class(obj, target_class, allow_none = False):
    """ Checks that the  obj is a (sub)type of target_class. 
        Raises a TypeError if this is not the case.
    """
    if not isinstance(obj, target_class):
        if not (allow_none and obj is None):
            raise TypeError("obj must be a of type {}, got: {}"
                            .format(target_class, type(obj)))    
    
    
def parse_assign_statement(statement):
    """ Parses an assign statement and returns tuple of inputs and a tuple of outputs
    """
    check_class(statement, ast.Assign)

    # Targets can have more than one element. E.g. when the statement is: a = b = 6
    # This is not supported (at the moment)
    if len(statement.targets) != 1:
        raise ValueError("Targets should be of length 1. Got: {}".format(len(statement.targets)))
    
    target = statement.targets[0]
    if not isinstance(target.ctx, ast.Store):
        raise ValueError("Target.ctx should be store. Got: {}".format(target.ctx))
    
    return target.id

    
def get_statements_from_code(code):
    """ Compiles the code string
        
        Verifies it consists of a list of statements and returns this list.
    """
    module = ast.parse(code, mode="exec")
    check_class(module, ast.Module)
    return module.body

    
def main():
    logging_basic_config("DEBUG")
    
    correct_code = ["a = 6; a2 = 5" , 
                    "b = -2", 
                    "c = a+3", 
                    "d = c * b", 
                    #"e, f = range(2)",
                    "l = [1,2,3]",  
                    "l[1] = 9"]
    self_ref_code = ["a = 6", "b = -2", "a=a+2"]
    code = "\n".join(correct_code)
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
