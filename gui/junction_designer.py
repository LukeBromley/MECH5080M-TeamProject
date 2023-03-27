from platform import system
if system() == 'Windows':
    import sys
    sys.path.append('./')

import sys
from PyQt5.QtWidgets import QStyleFactory

from library.model import Model

from gui.Tabs.pygame_graphics import *
from gui.Tabs.open_save_tab import *
from gui.Tabs.design_tab import *
from gui.Tabs.view_tab import *
from gui.Tabs.control_tab import *
from gui.Tabs.lane_changing_tab import *


class JunctionDesigner:
    def __init__(self) -> None:
        """

        Junction Designer allows the user to design and create a junction and view car positions.
        The window is based on PYQT and uses PyGame for rendering the graphics.
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

        Main GUI window used for junction designer. Contains all sub-widgets and visualiser model.

        """
        super(DesignerMainWindow, self).__init__()

        # Visualiser model
        self.model = Model()

        # Set Window size
        self.window_width, self.window_height = 1440, 847
        self.setMinimumSize(self.window_width, self.window_height)

        # Pygame graphics renderer class
        self.pygame_graphics = PygameGraphics(self.window_width, self.window_height, self.model)

        # Junction designer main widget
        self.main_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.main_widget)

        # Main layout.
        # HBox used for left side junction view and right side designer tabs
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
        self.view_tab = ViewTab(self, self.pygame_graphics.set_scale, self.pygame_graphics.update_map_image)
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

    def refresh_pygame_widget(self, force_full_refresh: bool = True) -> None:
        """

        Refreshes the pygame widget with the current graphics rendering. Junction paths are pre-rendered to improve
        performance but simpler elements (like nodes) are rendered on the refresh.

        A full refresh refreshes everything which is default behavior.

        :param force_full_refresh: Refreshes all surfaces
        :return: None
        """
        self.pygame_graphics.refresh(
            force_full_refresh=force_full_refresh,
            draw_map=self.view_tab.show_layer_map,
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

    def update_mouse_coords(self) -> None:
        """

        Update mouse coordinates shown in the design tab based on the location of the mouse click in the junction view
        window.

        :return: None
        """
        x, y = self.pygame_graphics.get_click_position()
        self.design_tab.coords.setText("Mouse Coords: (" + str(x) + ", " + str(y) + ")")

    def render_pygame_widget(self) -> None:
        """

        Renders all aspects of the visualiser that cannot be rendered on every refresh. This improves performance.
        Paths are pre-rendered because it is computationally intensive and does not need to happen on every refresh.

        :return: None
        """
        # Calculate all parameters for paths
        for path in self.model.paths:
            path.calculate_all(self.model)

        # Render all paths
        if len(self.model.paths) > 0:
            self.pygame_graphics.render_hermite_paths(self.model.paths)
        self.refresh_pygame_widget()

    def pygame_widget_scroll(self, event) -> None:
        """

        Passes PYQT scroll events onto the pygame graphics to compute graphical translation and updates widget

        :param event: PYQT mouse scroll event
        :return: None
        """
        self.pygame_graphics.calculate_scroll(event)
        self.refresh_pygame_widget()
        self.update_mouse_coords()

    def identify_path(self, path_uids: list) -> None:
        """

        Displays only the listed paths provided for 0.25s (longer because of rendering time)

        :param path_uids: list of path uids to highlight
        :return: None
        """
        paths = [self.model.get_path(path_uid) for path_uid in path_uids]
        self.pygame_graphics.highlight_paths(paths)
        self.pygame_widget.refresh(self.pygame_graphics.surface)
        self.timer = Timer(250, self.render_pygame_widget)

    def update_nodes_paths(self, nodes: list, paths: list) -> None:
        """

        Updates the list of nodes and paths stored in the model. If nodes are changed on the back-end then the
        widgets (on the front end) need updating. Unlike the visualiser, this must be completed independently.

        :param nodes: list of nodes
        :param paths: list of paths
        :return: None
        """
        self.model.nodes = nodes
        self.model.paths = paths

    def update_design_tab(self) -> None:
        """

        Updates the design tab based on the current model

        :return: None
        """
        self.design_tab.update_node_path_widgets()

    def update_control_tab(self) -> None:
        """

        Updates the control tab based on the current model

        :return: None
        """
        self.control_tab.set_add_light_button_state()

    def update_lights(self, lights: list) -> None:
        """

        Updates the list of lights stored in the model. If lights are changed on the back-end then the
        widgets (on the front end) need updating. Unlike the visualiser, this must be completed independently.

        :param lights: list of light objects
        :return: None
        """
        self.model.lights = lights

    def recenter(self) -> None:
        """

        Re-centers the viewer to center around 0,0.
        :return: None
        """
        self.pygame_graphics.recenter()
        self.refresh_pygame_widget()

