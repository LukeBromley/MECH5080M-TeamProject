from Frontend.Tabs.PYQTShortcuts import *
from PyQt5.QtCore import Qt
from Library.infrastructure import TrafficLight
from functools import partial
from math import pi


class ControlTab(QtWidgets.QWidget):
    def __init__(self, gui, model):
        """

        Control tab that allows the user to add traffic lights
        :param gui: parent gui class
        :param model: model
        """
        super(ControlTab, self).__init__()

        # Functions
        self.gui = gui
        self.model = model

        # Widgets + Layouts
        self.v_box = VBox(self, align=Qt.AlignTop)

        self.light_box = GroupBox(self, "Traffic Lights", layout=self.v_box)
        self.light_box_scroll = ScrollArea(self.light_box, self.light_box.v_box)
        self.add_light_button = Button(self.light_box, "Add Traffic Light", self.light_box.v_box)

        self.light_widgets = []

        # Connect callback functions of relevant widgets
        self._connect()
        self.set_add_light_button_state()

    def set_add_light_button_state(self) -> None:
        """

        Checks if the add traffic light button should be enabled or not based on if there are any paths
        :return: None
        """
        nodes, paths = self.model.nodes, self.model.paths
        if len(paths) > 0:
            self.add_light_button.setEnabled(True)
        else:
            self.add_light_button.setDisabled(True)

    def _connect(self) -> None:
        """

        Connects callback functions
        :return: None
        """
        self.add_light_button.pressed.connect(self.add_light)

    def update_light_widgets(self, lights: list) -> None:
        """

        Updates the view with all light data in the model
        :param lights: list of all lights
        :return: None
        """
        # Remove all current node and path widgets
        for i in reversed(range(self.light_box_scroll.v_box.count())):
            self.light_box_scroll.v_box.itemAt(i).widget().setParent(None)

        # Clear node and path widget lists
        self.light_widgets.clear()

        # Re-add all lights
        nodes, paths = self.model.nodes, self.model.paths
        for index, light in enumerate(reversed(lights)):
            self.light_widgets.append(TrafficLightWidget(self.light_box, self.light_box_scroll.v_box))
            self.light_widgets[-1].set_options(paths)
            self.light_widgets[-1].set_info(light.uid, light.paths)
            self.light_widgets[-1].connect_delete(partial(self.remove_light, light.uid))
            self.light_widgets[-1].connect_identify(partial(self.identify_light, light.uid))
            self.light_widgets[-1].connect_change(partial(self.update_traffic_light_data, light.uid, index))

    def update_traffic_light_data(self, uid: int, widget_index: int) -> None:
        """

        Updates the model with the current selection that the user has made in the view
        :param uid: UID of traffic light info to update
        :param widget_index: Index of traffic light widget with updated info
        :return: None
        """
        nodes, paths = self.model.nodes, self.model.paths
        lights = self.model.lights
        for light in lights:
            if light.uid == uid:
                light.paths.clear()
                all_items = [self.light_widgets[widget_index].selected_paths.model().item(i, 0) for i in range(self.light_widgets[widget_index].selected_paths.count())]
                for item in all_items:
                    if item.checkState() == QtCore.Qt.Checked:
                        for path in paths:
                            if path.uid == int(item.text()):
                                light.paths.append(path)
                                break

                if len(light.paths) > 0:
                    self.light_widgets[widget_index].identify.setEnabled(True)
                else:
                    self.light_widgets[widget_index].identify.setDisabled(True)

        self.set_add_light_button_state()

    def add_light(self) -> None:
        """

        Adds a light to the model and updates the view
        :return: None
        """
        lights = self.model.lights
        light_uid = 1
        if len(lights) > 0:
            light_uid = max([light.uid for light in lights]) + 1
        lights.append(TrafficLight(light_uid, None))
        self.gui.update_control_tab()
        self.update_light_widgets(lights)
        self.light_box_scroll.verticalScrollBar().setSliderPosition(0)

    def remove_light(self, uid: int) -> None:
        """

        Deletes a light
        :param uid: UID of light to delete
        :return: None
        """
        lights = self.model.lights

        for index, light in enumerate(lights):
            if light.uid == uid:
                lights.pop(index)
                break

        self.gui.update_control_tab(lights)
        self.update_light_widgets(lights)

    def identify_light(self, uid: int) -> None:
        """

        Creates a list of paths to identify when an identify button is pressed
        :param uid: UID of light that we want to identify the paths of
        :return: None
        """
        lights = self.model.lights
        for light in lights:
            if light.uid == uid:
                self.gui.identify_path(light.paths)
                break


class TrafficLightWidget(QtWidgets.QWidget):
    def __init__(self, parent_widget, layout=None) -> None:
        """

        PYQT widget for each traffic light
        :param parent_widget: widget that this widget belongs to
        :param layout: Layout where this widget is added
        """
        super().__init__(parent_widget)
        if layout is not None:
            layout.addWidget(self)

        # Widgets + Layouts
        self.h_box = HBox(self, align=Qt.AlignLeft)

        self.uid_label = Text(self, "Light ID: ", self.h_box)
        self.uid_edit = Text(self, "", self.h_box)

        self.selected_paths_label = Text(self, "Paths: ", self.h_box)
        self.selected_paths = TickableComboBox(self, self.h_box)
        self.selected_paths.setMinimumWidth(150)

        self.identify = Button(self, "Identify", self.h_box)
        self.identify.setDisabled(True)

        self.delete = Button(self, "Delete", self.h_box)

    def set_options(self, paths: list) -> None:
        """

        Adds all the options for the selected paths combo box
        :param paths: list of paths
        :return: None
        """
        for index, path in enumerate(paths):
            self.selected_paths.add_item(str(path.uid), index)

    def set_info(self, uid: int, selected_paths: list) -> None:
        """

        Sets the current model data for the paths
        :param uid: path uid
        :param selected_paths: list of all selected paths
        :return:
        """
        self.uid_edit.setText(str(uid))

        self.selected_paths.untick_all()
        for path in selected_paths:
            self.selected_paths.set_ticked(str(path.uid))

        if len(selected_paths) > 0:
            self.identify.setEnabled(True)
        else:
            self.identify.setDisabled(True)

    def connect_change(self, function) -> None:
        """

        Connects the callback functions for each light info changes
        :param function: callback function
        :return: None
        """
        self.selected_paths.currentIndexChanged.connect(function)

    def connect_identify(self, function) -> None:
        """

        Connects the callback function for light phase identification button
        :param function: callback function
        :return: None
        """
        self.identify.pressed.connect(function)

    def connect_delete(self, function) -> None:
        """

        Connects the callback function for deleting a light phase
        :param function: callback function
        :return: None
        """
        self.delete.pressed.connect(function)



