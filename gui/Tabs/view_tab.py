from gui.Tabs.pyqt_shortcuts import *
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFileDialog


class ViewTab(QtWidgets.QWidget):
    def __init__(self, gui, set_scale_function, update_map_function) -> None:
        """
        View tab that allows the user to show and hide layers, set scaling and reset
        :param gui: parent gui class
        :param set_scale_function: function that sets the scale of the gui

        """
        super(ViewTab, self).__init__()

        # Functions
        self.gui = gui
        self.set_scale_function = set_scale_function
        self.update_map_function = update_map_function

        # Widgets + Layouts
        self.v_box = VBox(self, align=Qt.AlignTop)

        #   View
        self.view_box = GroupBox(self, "View", layout=self.v_box)

        self.view_h_box = HBox(self, self.view_box.v_box, align=Qt.AlignLeft)
        self.scale_label = Text(self, "Scale: ", self.view_h_box)
        self.scale = SpinBox(self, self.view_h_box, min=25, max=400)
        self.scale.setValue(100)
        self.recenter_button = Button(self, "Recenter", layout=self.view_h_box)

        #   View
        self._latitude = -1.556358
        self._longitude = 53.810705
        self._heading = 50
        self._map_scale = 200

        self.map_box = GroupBox(self, "Map", layout=self.v_box)

        self.map_h_box = HBox(self, self.map_box.v_box, align=Qt.AlignLeft)
        self.map_latitude_label = Text(self, "Latitude: ", self.map_h_box)
        self.map_latitude = DecimalSpinBox(self, self.map_h_box, min=-90, max=90, number_of_decimal_places=6)
        self.map_longitude_label = Text(self, "Longitude: ", self.map_h_box)
        self.map_longitude = DecimalSpinBox(self, self.map_h_box, min=-180, max=180, number_of_decimal_places=6)
        self.map_heading_label = Text(self, "Heading: ", self.map_h_box)
        self.map_heading = SpinBox(self, self.map_h_box, min=0, max=359)
        self.map_scale_label = Text(self, "scale: ", self.map_h_box)
        self.map_scale = SpinBox(self, self.map_h_box, min=50, max=400)
        self.map_update_button = Button(self, "Update", layout=self.map_h_box)
        self.maps_api_key_label = Text(self, "Google Maps API Key", self.map_box.v_box)
        self.maps_api_key = TextEdit(self, self.map_box.v_box)
        self.map_box.setDisabled(True)
        self.set_map_coords()

        #   Layers
        self.layers_box = GroupBox(self, "Layers", layout=self.v_box)

        self.show_layer_map = False
        self.show_layer_grid = False
        self.show_layer_hermite_paths = True
        self.show_layer_nodes = True
        self.show_layer_labels = True
        self.show_layer_curvature = True
        self.show_layer_vehicles = True

        self.layer_map = TickBox(self, "Map", layout=self.layers_box.v_box)
        self.layer_grid = TickBox(self, "Grid", layout=self.layers_box.v_box)
        self.layer_hermite_paths = TickBox(self, "Hermite Paths", layout=self.layers_box.v_box)
        self.layer_nodes = TickBox(self, "Nodes", layout=self.layers_box.v_box)
        self.layer_labels = TickBox(self, "Labels", layout=self.layers_box.v_box)
        self.layer_curvature = TickBox(self, "Curvature", layout=self.layers_box.v_box)
        self.layer_vehicles = TickBox(self, "Cars", layout=self.layers_box.v_box)
        self.set_layer_states()

        # Playback
        self.playback_box = GroupBox(self, "Play", layout=self.v_box)
        self.playback_load_data = Button(self, "Load Data", self.playback_box.v_box)
        self.playback_scrub_bar = Slider(self, direction="h", layout=self.playback_box.v_box)
        self.h_box = HBox(self, self.playback_box.v_box)
        self.playback_prev_tick = Button(self, "<", self.h_box)
        self.playback_play_pause = Button(self, "Play", self.h_box)
        self.playback_next_tick = Button(self, ">", self.h_box)
        self.disable_playback()

        self.playback_timer = Timer(10, self.next_tick, single_shot=False)

        self.tick = 0
        self.playback_play = False
        self.playback_max_tick = 0
        self.tick_time = 0.01

        # Connect widget callback functions
        self.connect()

    def connect(self) -> None:
        """

        Connect widget callback functions
        :return: None
        """
        self.recenter_button.pressed.connect(self.gui.recenter)
        self.scale.valueChanged.connect(self.set_scale)

        self.map_update_button.pressed.connect(self.update_map_coords)

        self.layer_map.stateChanged.connect(self.update_layer_states)
        self.layer_grid.stateChanged.connect(self.update_layer_states)
        self.layer_hermite_paths.stateChanged.connect(self.update_layer_states)
        self.layer_nodes.stateChanged.connect(self.update_layer_states)
        self.layer_labels.stateChanged.connect(self.update_layer_states)
        self.layer_curvature.stateChanged.connect(self.update_layer_states)
        self.layer_vehicles.stateChanged.connect(self.update_layer_states)

        self.playback_load_data.pressed.connect(self.load_results_data)
        self.playback_next_tick.pressed.connect(self.next_tick)
        self.playback_prev_tick.pressed.connect(self.prev_tick)
        self.playback_play_pause.pressed.connect(self.play_pause)
        self.playback_scrub_bar.valueChanged.connect(self.scrub)

    def update_map_coords(self):
        self._latitude = self.map_latitude.value()
        self._longitude = self.map_longitude.value()
        self._heading = self.map_heading.value()
        self._map_scale = (self.map_scale.value() / 20) + 5
        maps_api_key = self.maps_api_key.text()
        self.update_map_function(self._latitude, self._longitude, self._heading, self._map_scale, maps_api_key)
        self.gui.refresh_pygame_widget()

    def set_map_coords(self):
        self.map_latitude.setValue(self._latitude)
        self.map_longitude.setValue(self._longitude)
        self.map_heading.setValue(self._heading)
        self.map_scale.setValue(self._map_scale)

    def update_layer_states(self) -> None:
        """

        Update the layer state variables with the state of the tick box widgets
        :return: None
        """

        self.show_layer_map = self.layer_map.isChecked()
        if self.show_layer_map:
            self.map_box.setEnabled(True)
        else:
            self.map_box.setDisabled(True)

        self.show_layer_grid = self.layer_grid.isChecked()
        self.show_layer_hermite_paths = self.layer_hermite_paths.isChecked()

        if self.layer_hermite_paths.isChecked():
            self.layer_curvature.setEnabled(True)
        else:
            self.layer_curvature.setDisabled(True)
            self.layer_curvature.setChecked(False)

        self.show_layer_nodes = self.layer_nodes.isChecked()
        self.show_layer_labels = self.layer_labels.isChecked()
        self.show_layer_curvature = self.layer_curvature.isChecked()
        self.show_layer_vehicles = self.layer_vehicles.isChecked()

        self.gui.refresh_pygame_widget()

    def set_layer_states(self) -> None:
        """

        Set tick box widgets with the state of the layer state variables
        :return: None
        """
        self.layer_map.setChecked(self.show_layer_map)
        self.layer_grid.setChecked(self.show_layer_grid)
        self.layer_hermite_paths.setChecked(self.show_layer_hermite_paths)
        self.layer_nodes.setChecked(self.show_layer_nodes)
        self.layer_labels.setChecked(self.show_layer_labels)
        self.layer_curvature.setChecked(self.show_layer_curvature)
        self.layer_vehicles.setChecked(self.show_layer_vehicles)

    def set_scale(self) -> None:
        """

        Sets the scale of the graphics.
        :return: None
        """
        scale = 0.2 * self.scale.value() / 100
        self.set_scale_function(scale)
        self.gui.refresh_pygame_widget()

    def disable_playback(self):
        self.playback_scrub_bar.setDisabled(True)
        self.playback_prev_tick.setDisabled(True)
        self.playback_play_pause.setDisabled(True)
        self.playback_next_tick.setDisabled(True)

    def enable_playback(self):
        self.playback_scrub_bar.setEnabled(True)
        self.playback_prev_tick.setEnabled(True)
        self.playback_play_pause.setEnabled(True)
        self.playback_next_tick.setEnabled(True)

    def load_results_data(self):
        file_path = QFileDialog.getOpenFileName(self, 'Open Results Data', '../junctions', "Results File (*.res)")[0]
        if len(file_path) > 0:
            self.gui.model.load_results(file_path)
        self.enable_playback()
        self.playback_max_tick = self.get_max_tick()
        self.playback_scrub_bar.setMaximum(self.playback_max_tick)

    def get_max_time(self):
        time = [vehicle.total_time(self.tick_time) for vehicle in self.gui.model.vehicle_results]
        return max(time)

    def get_max_tick(self):
        time = [vehicle.total_tick(self.tick_time) for vehicle in self.gui.model.vehicle_results]
        return max(time) - 1

    def get_time(self):
        return self.tick_time * self.tick

    def get_start_tick(self, time):
        return time / self.tick_time

    def next_tick(self):
        self.tick += 1
        if self.tick > self.playback_max_tick:
            self.tick = self.playback_max_tick
            self.playback_play = False
            self.playback_timer.stop()
            self.update_play_pause_button()
        self.update_playback_scroll()
        self.update_car_positions()

    def prev_tick(self):
        self.tick -= 1
        if self.tick < 0:
            self.tick = 0
        self.update_playback_scroll()
        self.update_car_positions()

    def play_pause(self):
        if self.playback_play:
            self.playback_timer.stop()
            self.playback_play = False
        else:
            self.playback_timer.start()
            self.playback_play = True
        self.update_play_pause_button()

    def scrub(self):
        self.tick = self.playback_scrub_bar.value()
        self.update_car_positions()

    def update_play_pause_button(self):
        if self.playback_play:
            self.playback_play_pause.setText("Pause")
        else:
            self.playback_play_pause.setText("Play")

    def update_playback_scroll(self):
        self.playback_scrub_bar.setValue(self.tick)

    def calculate_current_car_positions(self):
        car_positions = []
        for vehicle in self.gui.model.vehicle_results:
            if self.get_time() > vehicle.start_time:
                tick_delta = self.tick - vehicle.start_tick(self.tick_time)
                car_positions.append(vehicle.position_data[int(tick_delta)])
        return car_positions

    def update_car_positions(self):
        self.gui.model.vehicles = self.calculate_current_car_positions()
        self.gui.refresh_pygame_widget(force_full_refresh=False)






