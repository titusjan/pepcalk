""" pepcalk programm

TODO: ast.IfExp, complex numbers.

Applications:
    - Btw bonnetjes.
    - Compact calendar
    - Function viewers (sliders to tweak function parameters).
    - Signal processing
    - Dagobert
    - Measurement database

"""

from astviewer import view
from objbrowser import browse

from pepcalk.main_window import start
from pepcalk.utils import logging_basic_config 

import logging
logger = logging.getLogger(__name__)


TEST_PROGRAM = """
b = 2*a
a = 5
c = b+a
"""

def main():
    logging_basic_config("DEBUG")

    if 0:
        view(source_code = "a+b", mode="single", width=800, height=600)
    else:
        #browse(graph, obj_name="graph", show_root_node=True, show_special_methods = False)
        start(TEST_PROGRAM)
    
         

if __name__ == '__main__':
    main()
