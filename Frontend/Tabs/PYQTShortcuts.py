from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTransform

"""

The functions in this fie are modifications on existing PYQT "Widgets" which are combined together to form the GUI.
The modifications have been done to make creating the GUI more readable and require less commands.
Additional functionality (e.g. automatically adding itself to the specified layout) has been added to. 

"""


class Button(QtWidgets.QPushButton):
    def __init__(self, parent_widget, text, layout=None, width=None, height=None) -> None:
        super().__init__(parent_widget)
        self.setText(text)
        if layout is not None:
            layout.addWidget(self)
        if width is not None:
            self.setFixedWidth(width)
        if height is not None:
            self.setFixedHeight(height)


class ComboBox(QtWidgets.QComboBox):
    def __init__(self, parent_widget, layout=None):
        super().__init__(parent_widget)
        if layout is not None:
            layout.addWidget(self)

    def wheelEvent(self, event):
        event.ignore()


class GroupBox(QtWidgets.QGroupBox):
    def __init__(self, parent_widget, text, layout=None, ):
        super().__init__(text, parent_widget)
        if layout is not None:
            layout.addWidget(self)
        self.v_box = VBox(self)
        self.setLayout(self.v_box)

    def addWidget(self, widget):
        self.v_box.addWidget(widget)


class HBox(QtWidgets.QHBoxLayout):
    def __init__(self, parent_widget, layout=None, align=None):
        super().__init__(parent_widget)
        if layout is not None:
            try:
                layout.addWidget(self)
            except TypeError:
                layout.addLayout(self)
        if align is not None:
            self.setAlignment(align)


class NodeWidget(QtWidgets.QWidget):
    def __init__(self, parent_widget, layout=None):
        super().__init__(parent_widget)
        if layout is not None:
            layout.addWidget(self)

        self.h_box = HBox(self)

        self.node_label = TextEdit(self, self.h_box)

        self.x_label = Text(self, "X: ", self.h_box)
        self.node_x = SpinBox(self, self.h_box)

        self.y_label = Text(self, "Y: ", self.h_box)
        self.node_y = SpinBox(self, self.h_box)


class PyGameWidget(QtWidgets.QWidget):
    def __init__(self, parent=None, layout=None, connected_function=None):
        super(PyGameWidget, self).__init__(parent)
        if layout is not None:
            layout.addWidget(self)

        self.graphics = None
        self.connected_function = connected_function
        self.installEventFilter(self)

    def refresh(self, surface):
        w = surface.get_width()
        h = surface.get_height()
        data = surface.get_buffer().raw
        self.graphics = QtGui.QImage(data, w, h, QtGui.QImage.Format_RGB32)
        self.repaint()

    def paintEvent(self,event):
        qp = QtGui.QPainter()
        qp.begin(self)
        qp.drawImage(0, 0, self.graphics)
        qp.end()

    def eventFilter(self, obj, event):
        if self is obj:
            if event.type() == QtCore.QEvent.MouseButtonPress or event.type() == QtCore.QEvent.MouseButtonRelease or event.type() == QtCore.QEvent.MouseMove:
                if self.connected_function is not None:
                    self.connected_function(event)
        return super(PyGameWidget, self).eventFilter(obj, event)

    def connect(self, connected_function):
        self.connected_function = connected_function


class ScrollArea(QtWidgets.QScrollArea):
    def __init__(self, parent_widget, layout=None):
        super().__init__(parent_widget)
        if layout is not None:
            layout.addWidget(self)
        self.widget = QtWidgets.QWidget(self)
        self.v_box = VBox(self.widget, align=Qt.AlignTop)

        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setWidgetResizable(True)
        self.setWidget(self.widget)


class Slider(QtWidgets.QSlider):
    def __init__(self, parent_widget, direction="h", layout=None):
        if direction == "h":
            super().__init__(QtCore.Qt.Horizontal, parent_widget)
        elif direction == "v":
            super().__init__(QtCore.Qt.Vertical, parent_widget)
        else:
            super().__init__(parent_widget)
        if layout is not None:
            layout.addWidget(self)


class SpinBox(QtWidgets.QSpinBox):
    def __init__(self, parent_widget, layout=None, max=None, min=None):
        super().__init__(parent_widget)
        if layout is not None:
            layout.addWidget(self)
        if max is not None:
            self.setMaximum(max)
        if min is not None:
            self.setMinimum(min)

    def wheelEvent(self, event):
        event.ignore()


class DecimalSpinBox(QtWidgets.QDoubleSpinBox):
    def __init__(self, parent_widget, layout=None, max=None, min=None, number_of_decimal_places=2):
        super().__init__(parent_widget)
        if layout is not None:
            layout.addWidget(self)
        if max is not None:
            self.setMaximum(max)
        if min is not None:
            self.setMinimum(min)
        self.setDecimals(number_of_decimal_places)

    def wheelEvent(self, event):
        event.ignore()


class Tabs(QtWidgets.QTabWidget):
    def __init__(self, parent_widget, layout=None, height=None):
        super().__init__(parent_widget)
        if height is not None:
            self.setStyleSheet("QTabBar::tab {height: " + str(height) + "px}")
        if layout is not None:
            layout.addWidget(self)


class Text(QtWidgets.QLabel):
    def __init__(self, parent_widget, text, layout=None):
        super().__init__(parent_widget)
        self.setText(text)
        if layout is not None:
            layout.addWidget(self)


class TextEdit(QtWidgets.QLineEdit):
    def __init__(self, parent_widget, layout=None):
        super().__init__(parent_widget)
        if layout is not None:
            layout.addWidget(self)


class TickBox(QtWidgets.QCheckBox):
    def __init__(self, parent_widget, text, layout=None):
        super().__init__(parent_widget)
        self.setText(text)
        if layout is not None:
            layout.addWidget(self)


class TickableComboBox(QtWidgets.QComboBox):
    def __init__(self, parent_widget, layout=None):
        super().__init__(parent_widget)
        if layout is not None:
            layout.addWidget(self)

        self.view().pressed.connect(self.handleItemPressed)
        self.setModel(QtGui.QStandardItemModel(self))

    def handleItemPressed(self, index):
        item = self.model().itemFromIndex(index)
        if item.checkState() == QtCore.Qt.Checked:
            item.setCheckState(QtCore.Qt.Unchecked)
        else:
            item.setCheckState(QtCore.Qt.Checked)

    def add_item(self, text, index):
        self.addItem(str(text))
        item = self.model().item(index, 0)
        item.setCheckState(QtCore.Qt.Unchecked)

    def untick_all(self):
        for index in range(self.count()):
            item = self.model().item(index, 0)
            item.setCheckState(QtCore.Qt.Unchecked)

    def set_ticked(self, text):
        for index in range(self.count()):
            if self.itemText(index) == text:
                item = self.model().item(index, 0)
                item.setCheckState(QtCore.Qt.Checked)
                break

    def set_tnticked(self, text):
        for index in range(self.count()):
            if self.itemText(index) == text:
                item = self.model().item(index, 0)
                item.setCheckState(QtCore.Qt.Unchecked)
                break


class VBox(QtWidgets.QVBoxLayout):
    def __init__(self, parent_widget, layout=None, align=None):
        super().__init__(parent_widget)
        if layout is not None:
            try:
                layout.addWidget(self)
            except TypeError:
                layout.addLayout(self)
        if align is not None:
            self.setAlignment(align)


class Timer(QtCore.QTimer):
    def __init__(self, duration, connected_function, single_shot=True):
        super().__init__()
        if single_shot:
            self.singleShot(duration, connected_function)
        else:
            self.timeout.connect(connected_function)
            self.start(duration)




