
""" TableWidgetModel Class."""
import logging
from PySide import QtCore, QtGui 
from PySide.QtCore import Qt


logger = logging.getLogger(__name__)


class AssignmentDelegate(QtGui.QStyledItemDelegate):
    
    def createEditor(self, parent, option, index):

        editor = QtGui.QLineEdit(parent)
        return editor
    

    def setEditorData(self, editor, index):
        """ Sets the data to be displayed and edited by our custom editor. """
        value = index.model().data(index, QtCore.Qt.EditRole)
        editor.setText(value)
        

    def setModelData(self, editor, model, index):
        """ Get the data from our custom editor and stuffs it into the model.
        """
        value = editor.text()
        model.setData(index, value, QtCore.Qt.EditRole)

