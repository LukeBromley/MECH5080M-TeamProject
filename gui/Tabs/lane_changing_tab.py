from gui.Tabs.pyqt_shortcuts import *
from PyQt5.QtCore import Qt
from library.infrastructure import Node, Path
from functools import partial
from math import pi


class LaneChangingTab(QtWidgets.QWidget):
    def __init__(self, gui, model):
        """

        Lane Changing tab that allows the user to specify parallel paths that lane changes can occur between

        :param gui: parent gui class
        :param model: model
        """
        super(LaneChangingTab, self).__init__()

        # Parent GUI and parent model
        self.gui = gui
        self.model = model

        # Widgets + Layouts
        self.v_box = VBox(self, align=Qt.AlignTop)

        self.path_box = GroupBox(self, "Paths", layout=self.v_box)
        self.path_box_scroll = ScrollArea(self.path_box, self.path_box.v_box)
        self.clear_all_lanes_button = Button(self, "Clear All Paths", self.path_box.v_box)
        self.clear_all_lanes_button.pressed.connect(self.clear_all_lanes)

        self.path_widgets = []

    def update_lane_widgets(self) -> None:
        """

        Updates the widgets for the list of lanes in the model.

        :return: None
        """

        # Remove all current path widgets
        for i in reversed(range(self.path_box_scroll.v_box.count())):
            self.path_box_scroll.v_box.itemAt(i).widget().setParent(None)

        # Clear path widget lists
        self.path_widgets.clear()

        # Re-add all paths
        for index, path in enumerate(reversed(self.model.paths)):
            self.path_widgets.append(PathWidget(self.path_box, self.path_box_scroll.v_box))
            self.path_widgets[-1].set_options(path.uid, self.model.paths)
            self.path_widgets[-1].set_info(path.uid, path.parallel_paths)
            self.path_widgets[-1].connect_identify(partial(self.identify_path, path.uid))
            self.path_widgets[-1].connect_change(partial(self.update_path_data, path.uid, index))

    def update_path_data(self, uid: int, widget_index: int) -> None:
        """

        Updates a specific path to add all parallel paths. It also updates all parallel paths to have the original path
        as a parallel path. The model is updated.

        :param uid: UID of specific path of update
        :param widget_index: Widget of path to update
        :return: None
        """
        parallel_paths = []
        all_items = [self.path_widgets[widget_index].other_lanes.model().item(i, 0) for i in range(self.path_widgets[widget_index].other_lanes.count())]
        for item in all_items:
            if item.checkState() == QtCore.Qt.Checked:
                parallel_paths.append(int(item.text()))

        self.model.update_path(uid, parallel_paths=parallel_paths)

        for path_uid in parallel_paths:
            path = self.model.get_path(path_uid)
            if uid not in path.parallel_paths:
                new_parallel_paths = path.parallel_paths + [uid]
                self.model.update_path(path.uid, parallel_paths=new_parallel_paths)

        for index, path in enumerate(reversed(self.model.paths)):
            self.path_widgets[index].set_info(path.uid, path.parallel_paths)

    def identify_path(self, uid: int) -> None:
        """

        Creates a list of paths and its parallel paths to identify when an identify button is pressed. The paths will
        then be coloured pink for 0.25s.

        :param uid: UID of path that we want to identify the parallel paths of
        :return: None
        """
        path = self.model.get_path(uid)
        paths = [path.uid] + path.parallel_paths

        self.gui.identify_path(paths)

    def clear_all_lanes(self) -> None:
        """

        Removes all parallel paths from all paths in model.

        :return: None
        """
        for path in self.model.paths:
            path.parallel_paths.clear()
        self.update_lane_widgets()


class PathWidget(QtWidgets.QWidget):
    def __init__(self, parent_widget, layout=None) -> None:
        """

        Path widget that allows parallel paths to be specified.

        :param parent_widget: parent widget
        :param layout: layout that the widget is to be added to
        """
        super().__init__(parent_widget)
        if layout is not None:
            layout.addWidget(self)

        # Widgets + Layouts
        self.h_box = HBox(self, align=Qt.AlignLeft)
        self.uid_label = Text(self, "Path ID: ", self.h_box)
        self.uid_edit = Text(self, "", self.h_box)

        self.other_lanes_label = Text(self, "Lanes: ", self.h_box)
        self.other_lanes = TickableComboBox(self, self.h_box)
        self.other_lanes.setMinimumWidth(150)

        self.identify = Button(self, "Identify", self.h_box)

    def set_options(self, uid: int, paths: list) -> None:
        """

        Specifies all other lanes that can be set as parallel.

        :param uid: UID of the path
        :param paths: list of all other paths
        :return: None
        """
        for path in paths:
            if path.uid != uid:
                self.other_lanes.addItem(str(path.uid))
        self.other_lanes.untick_all()

    def set_info(self, uid: int, paths_selected: list) -> None:
        """

        Sets the current info of the path widget including its uid and all parallel paths selected.

        :param uid: UID of path
        :param paths_selected: All parallel paths
        :return: None
        """
        self.uid_edit.setText(str(uid))

        for path_uid in paths_selected:
            self.other_lanes.set_ticked(str(path_uid))

    def connect_change(self, function) -> None:
        """

        Connects the callback function triggered when a widget in the GUI has changed.
        The callback function should update the model and visualiser (if required).

        :param function: Change function
        :return: None
        """
        self.other_lanes.model().itemChanged.connect(function)

    def connect_identify(self, function) -> None:
        """

        Connects the callback function triggered when a path and its parallel paths needs to be identified in the
        viewer.

        :param function: identify function
        :return:None
        """
        self.identify.pressed.connect(function)
