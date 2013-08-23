
""" 
   Program that shows the program on the right and its abstract syntax tree (ast) on the left.
"""
import sys, logging, traceback

from PySide import QtCore, QtGui

from pepcalk.absynt import ast_to_str
from pepcalk.calculation import Calculation
from pepcalk.utils import check_class, class_name

logger = logging.getLogger(__name__)

DEBUGGING = False

PROGRAM_NAME = 'PepCalk'
PROGRAM_VERSION = '0.0.1'
ABOUT_MESSAGE = u"""%(prog)s version %(version)s
""" % {"prog": PROGRAM_NAME, "version": PROGRAM_VERSION}

# Tree column indices
COL_TARGET = 0
COL_SOURCE = 1
COL_VALUE = 2
COL_TYPE = 3
COL_ORDER = 4
N_COLS = 5

DEFAULT_COL_WIDTH = 150

# ColumnSettings is an simple settings object
# pylint: disable=R0903    
class ColumnSettings(object):
    """ Class that stores INITIAL column settings. """
    
    def __init__(self, width=DEFAULT_COL_WIDTH, visible=True, name=None):
        """ Constructor to set mandatory and default settings) """
        self.name = name
        self.visible = visible
        self.width = width
        self.toggle_action = None  # action to show/hide column
        self.toggle_function = None # function that shows/hides column
# pylint: enable=R0903    
        


def get_qapplication_instance():
    """ Returns the QApplication instance. Creates one if it doesn't exist.
    """
    app = QtGui.QApplication.instance()
    if app is None:
        app = QtGui.QApplication(sys.argv)
    check_class(app, QtGui.QApplication)
    return app


def start(*args, **kwargs):
    """ Opens a PepCalk main window
    """
    app = get_qapplication_instance()
    
    window = MainWindow(*args, **kwargs)
    window.show()
        
    logger.info("Starting the PepCalk viewer...")
    exit_code = app.exec_()
    logger.info("PepCalk done...")
    return exit_code


# The main window inherits from a Qt class, therefore it has many 
# ancestors public methods and attributes.
# pylint: disable=R0901, R0902, R0904, W0201, R0913 

class MainWindow(QtGui.QMainWindow):
    """ The main application.
    """
    def __init__(self, source_code = '', width = None, height = None):
        """ Constructor.
        
            If width and height are both set, the window is resized.
        """
        super(MainWindow, self).__init__()
        
        # Models
        self._calculation = Calculation(source_code)
        self._source_code = source_code
    
        # Table columns
        self.col_settings = [None] * N_COLS
        self.col_settings[COL_TARGET] = ColumnSettings(name = 'target', visible=True,  width=100)
        self.col_settings[COL_SOURCE] = ColumnSettings(name = 'source', visible=True)
        self.col_settings[COL_VALUE]  = ColumnSettings(name = 'value', visible=True)
        self.col_settings[COL_TYPE]   = ColumnSettings(name = 'type', visible=False)
        self.col_settings[COL_ORDER]  = ColumnSettings(name = 'order', visible=False)
        
        # Views
        self._setup_actions()
        self._setup_menu()
        self._setup_views()
        self.setWindowTitle('{}'.format(PROGRAM_NAME))
        
        # Update views
        self._fill_calc_table()
        
        if width and height:
            self.resize(width, height)
    
        
    def sizeHint(self):
        return QtCore.QSize(800, 600)
    
    
    def _setup_actions(self):
        """ Creates the MainWindow actions.
        """  
        # Create actions for the table columns from its settings.
        for col_idx, settings in enumerate(self.col_settings):
            settings.toggle_action = \
                QtGui.QAction("Show {} Column".format(settings.name), 
                              self, checkable=True, checked=True,
                              statusTip = "Shows or hides the {} column".format(settings.name))
            if col_idx >= 0 and col_idx <= 9:
                settings.toggle_action.setShortcut("Ctrl+{:d}".format(col_idx))
            settings.toggle_function = self._make_show_column_function(col_idx) # keep reference
            assert settings.toggle_action.toggled.connect(settings.toggle_function)
            

    def _setup_menu(self):
        """ Sets up the main menu.
        """
        file_menu = self.menuBar().addMenu("&File")
        file_menu.addAction("&New", self.new_file, "Ctrl+N")
        file_menu.addAction("&Open...", self.open_file, "Ctrl+O")
        #file_menu.addAction("C&lose", self.close_window, "Ctrl+W")
        file_menu.addAction("E&xit", self.quit_application, "Ctrl+Q")
        
        if DEBUGGING is True:
            file_menu.addSeparator()
            file_menu.addAction("&Test", self.my_test, "Ctrl+T")
        
        view_menu = self.menuBar().addMenu("&View")
        for _idx, settings in enumerate(self.col_settings):
            view_menu.addAction(settings.toggle_action)     
        
        self.menuBar().addSeparator()
        help_menu = self.menuBar().addMenu("&Help")
        help_menu.addAction('&About', self.about)


    def _setup_views(self):
        """ Creates the UI widgets. 
        """
        central_splitter = QtGui.QSplitter(self, orientation = QtCore.Qt.Vertical)
        self.setCentralWidget(central_splitter)
        central_layout = QtGui.QHBoxLayout()
        central_splitter.setLayout(central_layout)
        
        # Table widget
        self.calc_table = QtGui.QTableWidget()
        self.calc_table.setColumnCount(N_COLS)
        
        self.calc_table.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.calc_table.setHorizontalHeaderLabels([col.name for col in self.col_settings])
        for idx, settings in enumerate(self.col_settings):
            self.calc_table.setColumnWidth(idx, settings.width)
        central_layout.addWidget(self.calc_table)

        # Editor widget
        font = QtGui.QFont()
        font.setFamily('Courier')
        font.setFixedPitch(True)
        font.setPointSize(13)

        self.editor = QtGui.QPlainTextEdit()
        self.editor.setReadOnly(True)
        self.editor.setFont(font)
        self.editor.setWordWrapMode(QtGui.QTextOption.NoWrap)
        self.editor.setStyleSheet("selection-color: black; selection-background-color: yellow;")
        central_layout.addWidget(self.editor)
        
        # Splitter parameters
        central_splitter.setCollapsible(0, False)
        central_splitter.setCollapsible(1, False)
        central_splitter.setSizes([500, 500])
        central_splitter.setStretchFactor(0, 0.5)
        central_splitter.setStretchFactor(1, 0.5)
        
        # Connect signals
        #assert self.calc_table.currentItemChanged.connect(self.highlight_node)
        
    
    def new_file(self):
        """ Clears the widgets """
        self._calculation = Calculation()
        self._source_code = ""
        self.editor.clear()
        self._fill_calc_table()
        
    
    def open_file(self, file_name=None):
        """ Opens a new file. Show the open file dialog if file_name is None.
        """
        if not file_name:
            file_name = self._get_file_name_from_dialog()
        
        self._update_widgets(file_name)

    
    def _get_file_name_from_dialog(self):
        """ Opens a file dialog and returns the file name selected by the user
        """
        file_name, _ = QtGui.QFileDialog.getOpenFileName(self, "Open File", 
                                                         '', "Python Files (*.py);;All Files (*)")
        return file_name

    
    def _update_widgets(self, file_name):
        """ Reads source from a file and updates the tree and editor widgets.. 
        """            
        if file_name:
            self._load_file(file_name)
            
        self.setWindowTitle('{} - {}'.format(PROGRAM_NAME, self._file_name))
        self.editor.setPlainText(self._source_code)
        
        try:
            self._fill_calc_table()
        except StandardError, ex:
            if DEBUGGING:
                raise
            else:
                stack_trace = traceback.format_exc()
                msg = "Unable to parse file: {}\n\n{}\n\n{}" \
                    .format(self._file_name, ex, stack_trace)
                logger.exception(ex)
                QtGui.QMessageBox.warning(self, 'error', msg)
        
                
    def _load_file(self, file_name):
        """ Opens a file and sets self._file_name and self._source code if succesful
        """
        logger.debug("Opening {!r}".format(file_name))
        
        in_file = QtCore.QFile(file_name)
        if in_file.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text):
            text = in_file.readAll()
            try:
                source_code = str(text, encoding='ascii')  # Python 3
            except TypeError:
                source_code = str(text)                    # Python 2
                
            self._file_name = file_name
            self._source_code = source_code
            
        else:
            msg = "Unable to open file: {}".format(file_name)
            logger.warn(msg)
            QtGui.QMessageBox.warning(self, 'error', msg)
            
   
    
    def _fill_calc_table(self):
        """ Populates the calculation table.
        """
        self.calc_table.clearContents()    
        self.calc_table.setColumnCount(N_COLS)
        self.calc_table.setRowCount(len(self._calculation.assignments))
        row = 0
        for assignment in self._calculation.assignments:
            logger.debug("Filling row {}: {}".format(row, assignment))
            self.calc_table.setItem(row, COL_TARGET, 
                                    QtGui.QTableWidgetItem(assignment.target))
            self.calc_table.setItem(row, COL_SOURCE,   
                                    QtGui.QTableWidgetItem(assignment.source))
            self.calc_table.setItem(row, COL_VALUE,   
                                    QtGui.QTableWidgetItem(assignment.value))
            self.calc_table.setItem(row, COL_TYPE,   
                                    QtGui.QTableWidgetItem(class_name(assignment.value)))
            row += 1
            
 

    def _make_show_column_function(self, column_idx):
        """ Creates a function that shows or hides a column."""
        show_column = lambda checked: self.obj_tree.setColumnHidden(column_idx, not checked)
        return show_column
    
    
    def my_test(self):
        """ Function for testing """
        pass

    def about(self):
        """ Shows the about message window. """
        QtGui.QMessageBox.about(self, "About %s" % PROGRAM_NAME, ABOUT_MESSAGE)

    def close_window(self):
        """ Closes the window """
        self.close()
        
    def quit_application(self):
        """ Closes all windows """
        app = QtGui.QApplication.instance()
        app.closeAllWindows()

# pylint: enable=R0901, R0902, R0904, W0201

