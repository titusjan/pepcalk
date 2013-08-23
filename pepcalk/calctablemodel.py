""" TableWidgetModel Class."""
from PySide import QtCore

from pepcalk.utils import class_name

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
            if col == self.COL_TARGET:
                return assignment.target
            elif col == self.COL_SOURCE:
                return assignment.source
            elif col == self.COL_VALUE:
                return assignment.value
            elif col == self.COL_TYPE:
                class_name(assignment.value)
            else:
                return None


    def flags(self, index):
        """ Set the item flags at the given index. 
        """
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable


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
    
    