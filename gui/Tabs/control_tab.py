from gui.Tabs.pyqt_shortcuts import *
from PyQt5.QtCore import Qt
from library.infrastructure import TrafficLight
from functools import partial
from math import pi


class ControlTab(QtWidgets.QWidget):
    def __init__(self, gui, model):
        """

        Design tab that allows the user to add traffic lights to the junction.

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

        Checks if the add traffic light button should be enabled or not based on if there are any paths in the model.

        :return: None
        """
        paths = self.model.paths
        if len(paths) > 0:
            self.add_light_button.setEnabled(True)
        else:
            self.add_light_button.setDisabled(True)

    def _connect(self) -> None:
        """

        Connects the call back functions of buttons.

        :return: None
        """
        self.add_light_button.pressed.connect(self.add_light)

    def update_light_widgets(self) -> None:
        """

        Updates the widgets for the list of lights in the model.

        :return: None
        """
        # Remove all current node and path widgets
        for i in reversed(range(self.light_box_scroll.v_box.count())):
            self.light_box_scroll.v_box.itemAt(i).widget().setParent(None)

        # Clear node and path widget lists
        self.light_widgets.clear()

        # Re-add all lights
        for index, light in enumerate(reversed(self.model.lights)):
            self.light_widgets.append(TrafficLightWidget(self.light_box, self.light_box_scroll.v_box))
            self.light_widgets[-1].set_options(self.model.paths)
            self.light_widgets[-1].set_info(light.uid, light.path_uids)
            self.light_widgets[-1].connect_delete(partial(self.remove_light, light.uid))
            self.light_widgets[-1].connect_identify(partial(self.identify_light, light.uid))
            self.light_widgets[-1].connect_change(partial(self.update_traffic_light_data, light.uid, index))

    def update_traffic_light_data(self, uid: int, widget_index: int) -> None:
        """

        Updates the model with the current selection in the GUI.

        :param uid: uid of traffic light to update
        :param widget_index: index of widget in light widget list which represents the light
        :return: None
        """
        lights = self.model.lights
        for light in lights:
            if light.uid == uid:
                # Update model
                light.path_uids.clear()
                all_items = [self.light_widgets[widget_index].selected_paths.model().item(i, 0) for i in range(self.light_widgets[widget_index].selected_paths.count())]
                for item in all_items:
                    if item.checkState() == QtCore.Qt.Checked:
                        light.path_uids.append(int(item.text()))

                # Set identify light state
                if len(light.path_uids) > 0:
                    self.light_widgets[widget_index].identify.setEnabled(True)
                else:
                    self.light_widgets[widget_index].identify.setDisabled(True)

        self.set_add_light_button_state()

    def add_light(self) -> None:
        """

        Adds a new light to the list of lights and updates widgets
        :return: None
        """
        self.model.add_light([])
        self.gui.update_control_tab()
        self.update_light_widgets()
        self.light_box_scroll.verticalScrollBar().setSliderPosition(0)

    def remove_light(self, uid: int) -> None:
        """

        Removes the specified light from the list of lights and updates widgets
        :param uid: uid of light to delete
        :return: None
        """
        self.model.remove_light(uid)
        self.gui.update_control_tab()
        self.update_light_widgets()

    def identify_light(self, uid: int) -> None:
        """

        Creates a list of paths to identify when an light identify button is pressed.
        :param uid: uid of light that we want to identify the paths of
        :return: None
        """
        lights = self.model.lights
        for light in lights:
            if light.uid == uid:
                self.gui.identify_path(light.path_uids)
                break


class TrafficLightWidget(QtWidgets.QWidget):
    def __init__(self, parent_widget, layout=None) -> None:
        """

        Widget for representing a Light in the control tab.

        :param parent_widget: parent widget
        :param layout: layout for the widgets to be added to
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

        Adds all the options for the selected paths to combo box.
        :param paths: list of paths
        :return: None
        """
        for index, path in enumerate(paths):
            self.selected_paths.add_item(str(path.uid), index)

    def set_info(self, uid: int, selected_paths: list) -> None:
        """

        Sets the info to be displayed by the light widget. This will be updated using information from the model.

        :param uid: light uid
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

        Connects the callback function triggered when a widget in the GUI has changed.
        The callback function should update the model and visualiser (if required).
        :param function: callback function
        :return: None
        """
        self.selected_paths.currentIndexChanged.connect(function)

    def connect_identify(self, function) -> None:
        """

        Connects the callback function to trigger when the light identification button is selected in the GUI
        The callback function should update the model and visualiser (if required).
        :param function: callback function
        :return: None
        """
        self.identify.pressed.connect(function)

    def connect_delete(self, function) -> None:
        """

        Connects the callback function to trigger when the light is deleted by the GUI.
        The callback function should update the model and visualiser (if required).
        :param function: callback function
        :return: None
        """
        self.delete.pressed.connect(function)



