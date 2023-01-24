from Frontend.Tabs.PYQTShortcuts import *
from PyQt5.QtCore import Qt
from Library.infrastructure import Node, Path
from functools import partial
from math import pi


class DesignTab(QtWidgets.QWidget):
    def __init__(self, refresh_function, render_function, update_nodes_paths, get_nodes_paths):
        """

        :param refresh_function: function that refreshes the pygame graphics
        :param render_function: function that renders the pygame graphics
        :param update_nodes_paths: function that updates the nodes and paths in the top level class
        :param get_nodes_paths: function gets nodes and paths from the top level class
        """
        super(DesignTab, self).__init__()

        # Functions
        self._refresh_function = refresh_function
        self._render_function = render_function
        self._update_nodes_paths = update_nodes_paths
        self._get_nodes_paths = get_nodes_paths

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
        self.refresh_button.pressed.connect(self._render_function)
        self.add_node_button.pressed.connect(self.add_node)
        self.add_path_button.pressed.connect(self.add_path)

    def update_node_path_widgets(self, nodes: list, paths: list) -> None:
        """

        Updates the widgets for the list of nodes and paths with current node and path information
        :param nodes: list of all nodes
        :param paths: list of all paths
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
        for index, node in enumerate(reversed(nodes)):
            self.node_widgets.append(NodeWidget(self.node_box, self.node_box_scroll.v_box))
            self.node_widgets[-1].set_info(node.uid, node.x, node.y, node.angle * (360 / (2 * pi)))
            self.node_widgets[-1].connect_delete(partial(self.remove_node, node.uid))
            self.node_widgets[-1].connect_change(partial(self.update_node_data, node.uid, index))

        # Re-add all paths
        for index, path in enumerate(reversed(paths)):
            self.path_widgets.append(PathWidget(self.path_box, self.path_box_scroll.v_box))
            self.path_widgets[-1].set_info(path.uid, path.start_node.uid, path.end_node.uid, nodes)
            self.path_widgets[-1].connect_delete(partial(self.remove_path, path.uid))
            self.path_widgets[-1].connect_change(partial(self.update_path_data, path.uid, index))
            if path.start_node == path.end_node:
                self.path_widgets[-1].highlight_error()
            else:
                self.path_widgets[-1].unhighlight_error()

    def update_node_data(self, uid: int, widget_index: int) -> None:
        """

        Updates the coordinates of the specified node and recalculates the path coefficients of affected paths
        :param uid: uid of node to update
        :param widget_index: index of widget in node widget list which represents the node
        :return: None
        """
        nodes, paths = self._get_nodes_paths()
        for node in nodes:
            if node.uid == uid:
                node.x = self.node_widgets[widget_index].x_pos.value()
                node.y = self.node_widgets[widget_index].y_pos.value()
                node.angle = self.node_widgets[widget_index].angle.value() * ((2 * pi) / 360)
        self._update_nodes_paths(nodes, paths, refresh_widgets=False)

    def add_node(self) -> None:
        """

        Adds a new node to the list of nodes and updates widgets
        :return: None
        """
        nodes, paths = self._get_nodes_paths()
        node_uid = 1
        if len(nodes) > 0:
            node_uid = max([node.uid for node in nodes]) + 1
        nodes.append(Node(node_uid, 0, 0, 0))
        self._update_nodes_paths(nodes, paths)
        self.update_node_path_widgets(nodes, paths)
        self.node_box_scroll.verticalScrollBar().setSliderPosition(0)

    def remove_node(self, uid: int) -> None:
        """

        Removes the specified node from the list of nodes and updates widgets
        :param uid: uid of node to be removed
        :return: None
        """
        nodes, paths = self._get_nodes_paths()

        path_uids_to_remove = []
        for path in paths:
            if path.start_node.uid == uid or path.end_node.uid == uid:
                path_uids_to_remove.append(path.uid)

        for path_uid in path_uids_to_remove:
            self.remove_path(path_uid)

        for index, node in enumerate(nodes):
            if node.uid == uid:
                nodes.pop(index)
                break

        self._update_nodes_paths(nodes, paths)
        self.update_node_path_widgets(nodes, paths)

    def update_path_data(self, uid: int, widget_index: int) -> None:
        """

        Updates the nodes of the specified path and recalculates the path coefficients
        :param uid: uid of path to update
        :param widget_index: index of widget in path widget list which represents the path
        :return:
        """
        nodes, paths = self._get_nodes_paths()
        for path in paths:
            if path.uid == uid:
                for node in nodes:
                    if node.uid == int(self.path_widgets[widget_index].start_node.currentText()):
                        path.start_node = node
                        break
                for node in nodes:
                    if node.uid == int(self.path_widgets[widget_index].end_node.currentText()):
                        path.end_node = node
                        break

            if path.start_node == path.end_node:
                self.path_widgets[widget_index].highlight_error()
            else:
                self.path_widgets[widget_index].unhighlight_error()

        self._update_nodes_paths(nodes, paths, refresh_widgets=False)

    def add_path(self) -> None:
        """

        Adds a new path to the list of paths and updates widgets
        :return: None
        """
        nodes, paths = self._get_nodes_paths()
        path_uid = 1
        if len(paths) > 0:
            path_uid = max([path.uid for path in paths]) + 1
        paths.append(Path(path_uid, nodes[-1], nodes[-1]))

        self._update_nodes_paths(nodes, paths)
        self.update_node_path_widgets(nodes, paths)

    def remove_path(self, uid: int) -> None:
        """

        Removes the specified path from the list of paths and updates widgets
        :param uid: uid of path to be removed
        :return: None
        """
        nodes, paths = self._get_nodes_paths()

        for index, path in enumerate(paths):
            if path.uid == uid:
                paths.pop(index)
                break

        self._update_nodes_paths(nodes, paths)
        self.update_node_path_widgets(nodes, paths)


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
        self.order = Text(self, "Order: ", self.h_box)
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

    def set_info(self, uid: int, start_uid: object, end_uid: object, nodes: list, order: int) -> None:
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
        self.order.setText(str(order))

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




