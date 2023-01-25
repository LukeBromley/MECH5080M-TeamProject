import sys
from PyQt5.QtWidgets import QStyleFactory

from Tabs.PygameGraphics import *
from Tabs.OpenSaveTab import *
from Tabs.DesignTab import *
from Tabs.ViewTab import *
from Tabs.ControlTab import *

import threading


class JunctionDesigner:
    def __init__(self) -> None:
        """

        Class the executes the PYQT GUI
        Any code after this class will not be executed until the GUI window is closed.
        """
        # Create application
        self.application = QtWidgets.QApplication(sys.argv)
        self.application.setStyle('Windows')  # REQUIRED to show tickable combo boxes!!!!
        # Main window object + display it
        self.designer_window = DesignerMainWindow()
        self.designer_window.show()
        # Execute application
        self.application.exec_()


class DesignerMainWindow(QtWidgets.QMainWindow):
    def __init__(self) -> None:
        """

        Main GUI window.
        Contains all subwidgets
        """
        super(DesignerMainWindow, self).__init__()

        # List of all nodes and paths
        self.nodes = []
        self.paths = []
        self.lights = []
        self.cars = []

        # Set GUI window size
        self.window_width, self.window_height = 1440, 847
        self.setMinimumSize(self.window_width, self.window_height)

        # Pygame graphics renderer
        self.pygame_graphics = PygameGraphics(self.window_width, self.window_height, self.get_nodes_paths)

        # Set central widgets
        self.main_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.main_widget)

        # Widgets + Layouts
        self.h_box = HBox(self.main_widget)

        # Junction view widget
        self.pygame_widget = PyGameWidget(self.main_widget, layout=self.h_box)
        self.pygame_widget.connect(self.pygame_widget_scroll)
        self.pygame_widget.setFixedWidth(round(self.window_width / 2))

        # Tabs widget
        self.tabs = Tabs(self.main_widget, layout=self.h_box)

        # File management tab
        self.open_save_tab = OpenSaveTab(self.refresh_pygame_widget, self.render_pygame_widget, self.update_nodes_paths, self.get_nodes_paths, self.update_lights, self.get_lights)
        self.tabs.addTab(self.open_save_tab, "Open / Save")

        # Design tab
        self.design_tab = DesignTab(self.refresh_pygame_widget, self.render_pygame_widget, self.update_nodes_paths, self.get_nodes_paths)
        self.tabs.addTab(self.design_tab, "Design")

        # View tab
        self.view_tab = ViewTab(self.refresh_pygame_widget, self.render_pygame_widget, self.recenter, self.pygame_graphics.set_scale)
        self.tabs.addTab(self.view_tab, "View")

        # Control tab
        self.control_tab = ControlTab(self.refresh_pygame_widget, self.render_pygame_widget, self.identify_path, self.update_nodes_paths, self.get_nodes_paths, self.update_lights, self.get_lights)
        self.tabs.addTab(self.control_tab, "Control")
        self.timer = None

        # Initialise render
        self.render_pygame_widget()

    def refresh_pygame_widget(self) -> None:
        """

        Regresh pygame widget with current pygame graphics render.
        Paths are pre-rendered (improves performance).
        Nodes are not pre-rendered and instead are rendered on the refresh.
        Refresh handles scrolling and scaling.
        :return: None
        """
        self.pygame_graphics.refresh(
            draw_grid=self.view_tab.show_layer_grid,
            draw_hermite_paths=self.view_tab.show_layer_hermite_paths,
            draw_nodes=self.view_tab.show_layer_nodes,
            draw_node_labels=True if self.view_tab.show_layer_labels and self.view_tab.show_layer_nodes else False,
            draw_path_labels=True if self.view_tab.show_layer_labels and self.view_tab.show_layer_hermite_paths else False,
            draw_curvature=self.view_tab.show_layer_curvature,
        )
        self.pygame_widget.refresh(self.pygame_graphics.surface)
        x, y = self.pygame_graphics.get_click_position()
        self.design_tab.coords.setText("Mouse Coords: (" + str(x) + ", " + str(y) + ")")

    def render_pygame_widget(self) -> None:
        """

        Render the pygame graphics.
        Paths are pre-rendered because it is computationally intensive and does not need to happen on every refresh.
        :return: None
        """
        for path in self.paths:
            path.recalculate_coefs()

        if len(self.paths) > 0:
            self.pygame_graphics.render_hermite_paths(self.paths)
        self.refresh_pygame_widget()

    def pygame_widget_scroll(self, event) -> None:
        """

        Passes scroll events onto the pygame graphics and refresh the widget
        :param event: pyqt mouse scroll event
        :return: None
        """
        self.pygame_graphics.calculate_scroll(event)
        self.refresh_pygame_widget()

    def identify_path(self, paths: list) -> None:
        """

        Displays only the listed paths for 0.25s (seems to be more because of rendering time)
        :param paths: list of paths to highlight
        :return: None
        """
        self.pygame_graphics.highlight_paths(paths)
        self.pygame_widget.refresh(self.pygame_graphics.surface)
        self.timer = Timer(250, self.render_pygame_widget)

    def update_nodes_paths(self, nodes, paths, refresh_widgets=True):
        """

        Updates the list of nodes and paths
        :param nodes: list of nodes
        :param paths: list of paths
        :param refresh_widgets: If nodes are changed on the back-end then the widgets (on the front end) need updating
        :return:
        """
        self.nodes = nodes
        self.paths = paths
        if refresh_widgets:
            self.design_tab.update_node_path_widgets(self.nodes, self.paths)
        self.control_tab.set_add_light_button_state()

    def get_data(self) -> tuple:
        """

        :return: Returns the list of nodes and paths
        """
        return self.nodes, self.paths, self.cars

    def update_lights(self, lights: list, refresh_widgets: bool = True):
        """

        :param lights: list of light objects
        :param refresh_widgets: If lights are changed on the back-end then the widgets (on the front end) need updating
        :return: None
        """
        self.lights = lights
        if refresh_widgets:
            self.control_tab.update_light_widgets(self.lights)

    def get_lights(self):
        """

        :return: Returns the list of lights
        """
        return self.lights

    def recenter(self) -> None:
        """

        Re-center scrolling.
        :return: None
        """
        self.pygame_graphics.recenter()
        self.refresh_pygame_widget()
