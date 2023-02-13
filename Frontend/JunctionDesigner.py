from platform import system
if system() == 'Windows':
    import sys
    sys.path.append('./')

import sys
from Library.model import Model

from Frontend.Tabs.PygameGraphics import *
from Frontend.Tabs.OpenSaveTab import *
from Frontend.Tabs.DesignTab import *
from Frontend.Tabs.ViewTab import *
from Frontend.Tabs.ControlTab import *
from Frontend.Tabs.LaneChangingTab import *


class JunctionDesigner:
    def __init__(self) -> None:
        """

        Junction Designer allows the user to design and create a junction and view car positions.
        GUI uses PYQT with PyGame for visualiser on the backend.
        WARNING: Any code after this class will not be executed until the GUI window is closed.
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
        self.model = Model()

        # Set GUI window size
        self.window_width, self.window_height = 1440, 847
        self.setMinimumSize(self.window_width, self.window_height)

        # Pygame graphics renderer
        self.pygame_graphics = PygameGraphics(self.window_width, self.window_height, self.model)

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
        self.open_save_tab = OpenSaveTab(self, self.model)
        self.tabs.addTab(self.open_save_tab, "Open / Save")

        # Design tab
        self.design_tab = DesignTab(self, self.model)
        self.tabs.addTab(self.design_tab, "Design")

        # View tab
        self.view_tab = ViewTab(self, self.pygame_graphics.set_scale)
        self.tabs.addTab(self.view_tab, "View")

        # Control tab
        self.control_tab = ControlTab(self, self.model)
        self.tabs.addTab(self.control_tab, "Control")
        self.timer = None

        # Lane Changing tab
        self.lane_changing = LaneChangingTab(self, self.model)
        self.tabs.addTab(self.lane_changing, "Lane Changing")

        # Initialise render
        self.render_pygame_widget()

    def refresh_pygame_widget(self, force_full_refresh=True) -> None:
        """

        Regresh pygame widget with current pygame graphics render.
        Paths are pre-rendered (improves performance).
        Nodes are not pre-rendered and instead are rendered on the refresh.
        Refresh handles scrolling and scaling.
        :return: None
        """
        self.pygame_graphics.refresh(
            force_full_refresh=force_full_refresh,
            draw_grid=self.view_tab.show_layer_grid,
            draw_hermite_paths=self.view_tab.show_layer_hermite_paths,
            draw_nodes=self.view_tab.show_layer_nodes,
            draw_vehicles=self.view_tab.show_layer_vehicles,
            draw_node_labels=True if self.view_tab.show_layer_labels and self.view_tab.show_layer_nodes else False,
            draw_path_labels=True if self.view_tab.show_layer_labels and self.view_tab.show_layer_hermite_paths else False,
            draw_curvature=self.view_tab.show_layer_curvature,
            draw_lights=False
        )
        self.pygame_widget.refresh(self.pygame_graphics.surface)

    def update_mouse_coords(self):
        x, y = self.pygame_graphics.get_click_position()
        self.design_tab.coords.setText("Mouse Coords: (" + str(x) + ", " + str(y) + ")")

    def render_pygame_widget(self) -> None:
        """

        Render the pygame graphics.
        Paths are pre-rendered because it is computationally intensive and does not need to happen on every refresh.
        :return: None
        """
        for path in self.model.paths:
            path.calculate_all(self.model)

        if len(self.model.paths) > 0:
            self.pygame_graphics.render_hermite_paths(self.model.paths)
        self.refresh_pygame_widget()

    def pygame_widget_scroll(self, event) -> None:
        """

        Passes scroll events onto the pygame graphics and refresh the widget
        :param event: pyqt mouse scroll event
        :return: None
        """
        self.pygame_graphics.calculate_scroll(event)
        self.refresh_pygame_widget()
        self.update_mouse_coords()

    def identify_path(self, path_uids: list) -> None:
        """

        Displays only the listed paths for 0.25s (seems to be more because of rendering time)
        :param paths: list of paths to highlight
        :return: None
        """
        paths = [self.model.get_path(path_uid) for path_uid in path_uids]
        self.pygame_graphics.highlight_paths(paths)
        self.pygame_widget.refresh(self.pygame_graphics.surface)
        self.timer = Timer(250, self.render_pygame_widget)

    def update_nodes_paths(self, nodes, paths):
        """

        Updates the list of nodes and paths
        :param nodes: list of nodes
        :param paths: list of paths
        :return:
        """
        self.model.nodes = nodes
        self.model.paths = paths

    def update_design_tab(self):
        """

        :return: Updates the design tab with models nodes and paths
        """
        self.design_tab.update_node_path_widgets()

    def update_control_tab(self):
        """

        :return: Updates the control tab with models nodes and paths
        """
        self.control_tab.set_add_light_button_state()

    def update_lights(self, lights: list):
        """

        :param lights: list of light objects
        :return: None
        """
        self.model.lights = lights

    def recenter(self) -> None:
        """

        Re-center scrolling.
        :return: None
        """
        self.pygame_graphics.recenter()
        self.refresh_pygame_widget()
