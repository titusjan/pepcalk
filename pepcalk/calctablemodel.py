""" TableWidgetModel Class."""
import logging
from PySide import QtCore 
from PySide.QtCore import Qt
from pepcalk.utils import class_name

logger = logging.getLogger(__name__)

class CalcTableModel(QtCore.QAbstractTableModel):
    """"The modal class for the table vis widget
    
    """
    COL_ORDER = 0
    COL_TARGET = 1
    COL_SOURCE = 2
    COL_VALUE = 3
    COL_TYPE = 4
    N_COLS = 5
    
    HEADERS = [None] * N_COLS 
    HEADERS[COL_ORDER]  = 'Order'
    HEADERS[COL_TARGET] = 'Target'
    HEADERS[COL_SOURCE] = 'Source'
    HEADERS[COL_VALUE]  = 'Value'
    HEADERS[COL_TYPE]   = 'Type'

    
    def __init__(self, calculation = None, parent = None):
        """Init method
        """
        super(CalcTableModel, self).__init__(parent)
        self._calculation = calculation


    def data(self, index,  role = QtCore.Qt.DisplayRole):
        """reimplementation of data method from QAbstractTableModel
        """
        if not index.isValid():
            return None
        
        row = index.row()
        col = index.column()
        
        if (row < 0 or row >= len(self._calculation)): 
            return None
        
        if role == QtCore.Qt.DisplayRole:
            assignment = self._calculation.assignments[row]
            if col == self.COL_ORDER:
                return str(assignment.order_str)
            elif col == self.COL_TARGET:
                return assignment.target
            elif col == self.COL_SOURCE:
                return assignment.source
            elif col == self.COL_VALUE:
                return assignment.value
            elif col == self.COL_TYPE:
                if assignment.value is None:
                    return ""
                else:
                    return class_name(assignment.value)
            else:
                return None


    def flags(self, index):
        """ Set the item flags at the given index. 
        """
        col = index.column()
        if col == self.COL_TARGET or col == self.COL_SOURCE:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable
        else:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable


    def headerData(self, section, orientation, role):
        """ Sets the horizontal header (no vertical header)
        """
        if role != QtCore.Qt.DisplayRole or orientation == QtCore.Qt.Vertical:
            return None
        else:
            return self.HEADERS[section]

    
    def rowCount(self, _parent):
        " Number of rows"
        return len(self._calculation)


    def columnCount(self, _parent):
        " Number of columns"
        return self.N_COLS
    
    
    def setData(self, index, value, role=Qt.EditRole):
        """ Sets the role data for the item at index to value.

            Returns True if successful; otherwise returns False
        """
        if not (role == Qt.EditRole and
                index.isValid() and 
                (0 <= index.row() < len(self._calculation))):
            return False
        
        assignment = self._calculation.assignments[index.row()]
        if index.column() == self.COL_TARGET:
            logger.debug("setData target row = {}".format(index.row()))
            assignment.init_from_code("{} = {}".format(value, assignment.source))
        elif index.column() == self.COL_SOURCE:
            logger.debug("setData source row = {}".format(index.row()))
            assignment.init_from_code("{} = {}".format(assignment.target, value))
        else:
            return False

        self._calculation.compile()
        self._calculation.execute()
        self.emitAllDataChanged()
        return True
        
        
    def emitAllDataChanged(self):
        """ Emits the dataChanged signal for the complete table
        """
        top_left_index = self.index(0, 0)
        bottom_right_index = self.index(len(self._calculation) - 1, self.N_COLS - 1)
        self.dataChanged.emit(top_left_index, bottom_right_index) 

