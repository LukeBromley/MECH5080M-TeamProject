from Frontend.Tabs.PYQTShortcuts import *
from PyQt5.QtCore import Qt


class ViewTab(QtWidgets.QWidget):
    def __init__(self, refresh_function, render_function, recenter_function) -> None:
        """

        :param refresh_function: function that refreshes the pygame graphics
        :param render_function: function that renders the pygame graphics
        :param recenter_function: function to recenter junction scrolling
        """
        super(ViewTab, self).__init__()

        # Functions
        self.refresh_function = refresh_function
        self.render_function = render_function
        self.recenter_function = recenter_function

        # Scale
        self.scale_perc = 100

        # Widgets + Layouts
        self.v_box = VBox(self, align=Qt.AlignTop)

        #   View
        self.view_box = GroupBox(self, "View", layout=self.v_box)

        self.view_h_box = HBox(self, self.view_box.v_box, align=Qt.AlignLeft)
        self.scale_label = Text(self, "Scale %: ", self.view_h_box)
        self.scale = SpinBox(self, self.view_h_box, max=200, min=25)
        self.recenter_button = Button(self, "Recenter", layout=self.view_h_box)

        #   Layers
        self.layers_box = GroupBox(self, "Layers", layout=self.v_box)

        self.show_layer_grid = False
        self.show_layer_hermite_paths = True
        self.show_layer_poly_paths = False
        self.show_layer_nodes = True
        self.show_layer_labels = True
        self.show_layer_curvature = False
        self.show_layer_cars = False

        self.layer_grid = TickBox(self, "Grid", layout=self.layers_box.v_box)
        self.layer_hermite_paths = TickBox(self, "Hermite Paths", layout=self.layers_box.v_box)
        self.layer_poly_paths = TickBox(self, "Poly Paths", layout=self.layers_box.v_box)
        self.layer_nodes = TickBox(self, "Nodes", layout=self.layers_box.v_box)
        self.layer_labels = TickBox(self, "Labels", layout=self.layers_box.v_box)
        self.layer_curvature = TickBox(self, "Curvature", layout=self.layers_box.v_box)
        self.layer_cars = TickBox(self, "Cars", layout=self.layers_box.v_box)
        self.set_layer_states()

        # Playback
        self.play_box = GroupBox(self, "Play", layout=self.v_box)
        self.play_load_data = Button(self, "Load Data", self.play_box.v_box)
        self.play_scroll = Slider(self, direction="h", layout=self.play_box.v_box)
        self.h_box = HBox(self, self.play_box.v_box)
        self.play_prev_tick = Button(self, "<", self.h_box)
        self.play_play_pause = Button(self, "Play", self.h_box)
        self.play_next_tick = Button(self, ">", self.h_box)

        # Connect widget callback functions
        self.connect()

    def connect(self) -> None:
        """

        Connect widget callback functions
        :return: None
        """
        self.scale.valueChanged.connect(self.refresh_function)
        self.recenter_button.pressed.connect(self.recenter_function)

        self.layer_grid.stateChanged.connect(self.update_layer_states)
        self.layer_hermite_paths.stateChanged.connect(self.update_layer_states)
        self.layer_poly_paths.stateChanged.connect(self.update_layer_states)
        self.layer_nodes.stateChanged.connect(self.update_layer_states)
        self.layer_labels.stateChanged.connect(self.update_layer_states)
        self.layer_curvature.stateChanged.connect(self.update_layer_states)
        self.layer_cars.stateChanged.connect(self.update_layer_states)

    def update_layer_states(self) -> None:
        """

        Update the layer state variables with the state of the tick box widgets
        :return: None
        """
        self.scale_perc = self.scale.value()

        self.show_layer_grid = self.layer_grid.isChecked()
        self.show_layer_hermite_paths = self.layer_hermite_paths.isChecked()
        self.show_layer_poly_paths = self.layer_poly_paths.isChecked()

        if self.layer_hermite_paths.isChecked():
            self.layer_curvature.setEnabled(True)
        else:
            self.layer_curvature.setDisabled(True)
            self.layer_curvature.setChecked(False)

        self.show_layer_nodes = self.layer_nodes.isChecked()
        self.show_layer_labels = self.layer_labels.isChecked()
        self.show_layer_curvature = self.layer_curvature.isChecked()
        self.show_layer_cars = self.layer_cars.isChecked()

        self.refresh_function()

    def set_layer_states(self) -> None:
        """

        Set tick box widgets with the state of the layer state variables
        :return: None
        """
        self.scale.setValue(self.scale_perc)

        self.layer_grid.setChecked(self.show_layer_grid)
        self.layer_hermite_paths.setChecked(self.show_layer_hermite_paths)
        self.layer_poly_paths.setChecked(self.show_layer_poly_paths)
        self.layer_nodes.setChecked(self.show_layer_nodes)
        self.layer_labels.setChecked(self.show_layer_labels)
        self.layer_curvature.setChecked(self.show_layer_curvature)
        self.layer_cars.setChecked(self.show_layer_cars)
