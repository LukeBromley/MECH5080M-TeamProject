from Frontend.Tabs.PYQTShortcuts import *
from PyQt5.QtCore import Qt
from Library.infrastructure import Node, Path
from functools import partial
from math import pi


class DesignTab(QtWidgets.QWidget):
    def __init__(self, gui, model):
        """

        Design tab that allows the user to add paths or nodes
        :param gui: parent gui class
        :param model: model
        """
        super(DesignTab, self).__init__()

        self.gui = gui
        self.model = model

        # Widgets + Layouts
        self.v_box = VBox(self, align=Qt.AlignTop)

        self.coords = Text(self, "Mouse Coords: ", layout=self.v_box)

        self.refresh_button = Button(self, "Refresh View", layout=self.v_box)

        self.node_box = GroupBox(self, "Nodes", layout=self.v_box)
        self.node_box_scroll = ScrollArea(self.node_box, self.node_box.v_box)
        self.add_node_button = Button(self.node_box, "Add Node", self.node_box.v_box)

        self.node_widgets = []

        self.path_box = GroupBox(self, "Paths", layout=self.v_box)
        self.path_box_scroll = ScrollArea(self.path_box, self.path_box.v_box)
        self.add_path_button = Button(self.path_box, "Add Path", self.path_box.v_box)

        self.path_widgets = []

        # Connect callback functions of relevant widgets
        self._connect()

    def _connect(self) -> None:
        """

        Connects the call back functions of buttons
        :return: None
        """
        self.refresh_button.pressed.connect(self.gui.render_pygame_widget)
        self.add_node_button.pressed.connect(self.add_node)
        self.add_path_button.pressed.connect(self.add_path)

    def update_node_path_widgets(self) -> None:
        """

        Updates the widgets for the list of nodes and paths in the model
        :return: None
        """
        # Remove all current node and path widgets
        for i in reversed(range(self.node_box_scroll.v_box.count())):
            self.node_box_scroll.v_box.itemAt(i).widget().setParent(None)
        for i in reversed(range(self.path_box_scroll.v_box.count())):
            self.path_box_scroll.v_box.itemAt(i).widget().setParent(None)

        # Clear node and path widget lists
        self.node_widgets.clear()
        self.path_widgets.clear()

        # Re-add all nodes
        for index, node in enumerate(reversed(self.model.nodes)):
            self.node_widgets.append(NodeWidget(self.node_box, self.node_box_scroll.v_box))
            self.node_widgets[-1].set_info(node.uid, node.x, node.y, node.angle * (360 / (2 * pi)))
            self.node_widgets[-1].connect_delete(partial(self.remove_node, node.uid))
            self.node_widgets[-1].connect_change(partial(self.update_node_data, node.uid, index))

        # Re-add all paths
        for index, path in enumerate(reversed(self.model.paths)):
            self.path_widgets.append(PathWidget(self.path_box, self.path_box_scroll.v_box))
            self.path_widgets[-1].set_info(path.uid, path.start_node, path.end_node, self.model.nodes)
            self.path_widgets[-1].connect_delete(partial(self.remove_path, path.uid))
            self.path_widgets[-1].connect_change(partial(self.update_path_data, path.uid, index))
            if path.start_node == path.end_node:
                self.path_widgets[-1].highlight_error()
            else:
                self.path_widgets[-1].unhighlight_error()

        # Enable / Disable paths
        self.add_path_button.setEnabled(True if len(self.model.nodes) > 1 else False)

    def update_node_data(self, uid: int, widget_index: int) -> None:
        """

        Updates the coordinates of the specified node and recalculates the path coefficients of affected paths
        :param uid: uid of node to update
        :param widget_index: index of widget in node widget list which represents the node
        :return: None
        """
        x = self.node_widgets[widget_index].x_pos.value()
        y = self.node_widgets[widget_index].y_pos.value()
        angle = self.node_widgets[widget_index].angle.value() * ((2 * pi) / 360)

        self.model.update_node(uid, x, y, angle)

    def add_node(self) -> None:
        """

        Adds a new node to the list of nodes and updates widgets
        :return: None
        """

        self.model.add_node(0, 0, 0)
        self.update_node_path_widgets()
        self.node_box_scroll.verticalScrollBar().setSliderPosition(0)

    def remove_node(self, uid: int) -> None:
        """

        Removes the specified node from the list of nodes and updates widgets
        :param uid: uid of node to be removed
        :return: None
        """
        self.model.remove_node(uid)
        self.update_node_path_widgets()

    def update_path_data(self, uid: int, widget_index: int) -> None:
        """

        Updates the nodes of the specified path and recalculates the path coefficients
        :param widget_index: index of widget in path widget list which represents the path
        :return:
        """

        start_node = int(self.path_widgets[widget_index].start_node.currentText())
        end_node = int(self.path_widgets[widget_index].end_node.currentText())

        self.model.update_path(uid, start_node, end_node)

        if start_node == end_node:
            self.path_widgets[widget_index].highlight_error()
        else:
            self.path_widgets[widget_index].unhighlight_error()

    def add_path(self) -> None:
        """

        Adds a new path to the list of paths and updates widgets
        :return: None
        """
        self.model.add_path(self.model.nodes[-1].uid, self.model.nodes[-2].uid)
        self.update_node_path_widgets()

    def remove_path(self, uid: int) -> None:
        """

        Removes the specified path from the list of paths and updates widgets
        :param uid: uid of path to be removed
        :return: None
        """
        self.model.remove_path(uid)
        self.update_node_path_widgets()


class NodeWidget(QtWidgets.QWidget):
    def __init__(self, parent_widget, layout=None) -> None:
        """

        :param parent_widget: parent widget
        :param layout: layout for the widgets to be added to
        :return: None
        """
        super().__init__(parent_widget)
        if layout is not None:
            layout.addWidget(self)

        # Widgets + Layouts
        self.h_box = HBox(self, align=Qt.AlignLeft)
        self.uid_label = Text(self, "Node ID: ", self.h_box)
        self.uid_edit = Text(self, "", self.h_box)
        self.x_label = Text(self, "X: ", self.h_box)
        self.x_pos = SpinBox(self, self.h_box, 1000, -1000)
        self.x_pos.setValue(0)
        self.y_label = Text(self, "Y: ", self.h_box)
        self.y_pos = SpinBox(self, self.h_box, 1000, -1000)
        self.y_pos.setValue(0)
        self.ang_label = Text(self, "Angle: ", self.h_box)
        self.angle = SpinBox(self, self.h_box, 360, 0)
        self.delete = Button(self, "Delete", self.h_box)

    def set_info(self, uid: int, x: int, y: int, ang: int) -> None:
        """

        :param uid: set uid info display
        :param x: set x position to display
        :param y: set y position to display
        :param ang: set angle to display
        :return: None

        """
        self.uid_edit.setText(str(uid))
        self.x_pos.setValue(int(x))
        self.y_pos.setValue(int(y))
        self.angle.setValue(int(ang))

    def connect_change(self, function) -> None:
        """

        :param function: function to trigger when a parameter has been changed by the GUI
        :return: None
        """
        self.x_pos.valueChanged.connect(function)
        self.y_pos.valueChanged.connect(function)
        self.angle.valueChanged.connect(function)

    def connect_delete(self, function) -> None:
        """

        :param function: function to trigger when the node is deleted by the GUI
        :return: None
        """
        self.delete.pressed.connect(function)


class PathWidget(QtWidgets.QWidget):
    def __init__(self, parent_widget, layout=None) -> None:
        """

        :param parent_widget: parent widget
        :param layout: layout for the widgets to be added to
        :return: None

        """
        super().__init__(parent_widget)
        if layout is not None:
            layout.addWidget(self)

        # Widgets + Layouts
        self.h_box = HBox(self, align=Qt.AlignLeft)
        self.uid_label = Text(self, "Path ID: ", self.h_box)
        self.uid_edit = Text(self, "", self.h_box)
        self.start_node_label = Text(self, "From: ", self.h_box)
        self.start_node = ComboBox(self, self.h_box)
        self.end_node_label = Text(self, "To: ", self.h_box)
        self.end_node = ComboBox(self, self.h_box)
        self.delete = Button(self, "Delete", self.h_box)
        # self.car_spawner = TickBox(self, "Car")

    def highlight_error(self) -> None:
        """
        Highlight the uid label to indicate that the path from and to node are the same
        :return: None
        """
        self.uid_label.setStyleSheet("background-color: red;")

    def unhighlight_error(self) -> None:
        """
        Undo the actions of the highlight_error() method
        :return: None
        """
        self.uid_label.setStyleSheet("background: transparent;")

    def set_info(self, uid: int, start_uid: object, end_uid: object, nodes: list) -> None:
        """

        :param uid: set uid info to display
        :param start_uid: set start node uid to display
        :param end_uid: set end node uid to display
        :param nodes: list of all nodes
        :return: None
        """
        self.uid_edit.setText(str(uid))
        for node in nodes:
            self.start_node.addItem(str(node.uid))
            self.end_node.addItem(str(node.uid))
        self.start_node.setCurrentText(str(start_uid))
        self.end_node.setCurrentText(str(end_uid))

    def connect_change(self, function) -> None:
        """
        :param function: function to trigger when a parameter has been changed by the GUI
        :return: None
        """
        self.start_node.currentIndexChanged.connect(function)
        self.end_node.currentIndexChanged.connect(function)

    def connect_delete(self, function) -> None:
        """

        :param function: function to trigger when the path is deleted by the GUI
        :return: None
        """
        self.delete.pressed.connect(function)




