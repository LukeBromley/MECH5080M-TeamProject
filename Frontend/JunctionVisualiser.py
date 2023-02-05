import sys
from .Tabs.PygameGraphics import *
from .Tabs.ControlTab import *
from PyQt5.QtCore import QThread, QObject, pyqtSignal
from Library.FileManagement import *
from Library.maths import clamp
from Library.model import Model


class JunctionVisualiser:
    def __init__(self) -> None:
        """


        Junction Visualiser is a stripped down version of Junction Designer that allows the user to view the junction
        and cars in real time.
        GUI uses PYQT with PyGame for visualiser on the backend.
        GUI is threadded to allow the simulation to run on another thread.
        """
        # Create application
        self.application = QtWidgets.QApplication(sys.argv)
        self.application.setStyle('Windows')  # REQUIRED to show tickable combo boxes!!!!
        # Main window object + display it
        self.viewer_window = ViewerMainWindow()
        # Main Thread
        self.thread = QThread()
        self.worker = Run_Time_Function()
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

    def load_junction(self, junction_file_path: str) -> None:
        """

        Load junction
        :param junction_file_path: file path of junction to show
        :return: None
        """
        self.viewer_window.model.load_junction(junction_file_path, quick_load=True)
        self.viewer_window.render_pygame_widget()

    def define_main(self, main_function) -> None:
        """

        Defines the main function to run on the thread
        :param function: Main function
        :return: None
        """
        self.worker.set_main_function(main_function)

    def open(self) -> None:
        """

        Open the Junction Visualiser and start running the main function
        :return: None
        """
        self.thread.start()
        self.viewer_window.show()
        self.application.exec_()

    def update_vehicle_positions(self, vehicle_positions: list) -> None:
        """

        Updates the GUI car positions with a list of x, y coordinates
        :param car_positions: list of x,y car positions
        :return: None
        """
        self.viewer_window.model.vehicles = vehicle_positions

    def update_light_colours(self, lights: list) -> None:
        """

        Updates the GUI car positions with a list of x, y coordinates
        :param car_positions: list of x,y car positions
        :return: None
        """
        self.viewer_window.model.lights = lights

    def update_time(self, time):
        seconds = time.total_seconds()
        colour_mag = 255 - (255 * abs((seconds - (12 * 60 * 60)) / (12 * 60 * 60)))
        self.viewer_window.pygame_graphics.background_colour = (colour_mag, colour_mag, colour_mag)

    def update_collision_warning(self, collision):
        if collision:
            self.viewer_window.pygame_graphics.background_colour = (255, 0, 0)

    def set_scale(self, scale: int) -> None:
        """

        Sets GUI scale
        :param scale: scale %
        :return: None
        """
        scale = clamp(scale, 10, 200)
        scale = 0.2 * scale / 100
        self.viewer_window.pygame_graphics.set_scale(scale)


class Run_Time_Function(QObject):
    finished = pyqtSignal()
    def __init__(self):
        """

        Class to run on second thread that handles simulation
        """
        super().__init__()
        self.main_function = None

    def run(self) -> None:
        """

        Runs the main function and closes thread when function is complete
        :return: None
        """
        self.main_function()

    def set_main_function(self, main_function) -> None:
        """

        :param main_function:
        :return: None
        """
        self.main_function = main_function


class ViewerMainWindow(QtWidgets.QMainWindow):
    def __init__(self) -> None:
        """

        Main GUI window.
        Contains all subwidgets
        """
        super(ViewerMainWindow, self).__init__()

        # List of all nodes and paths
        self.model = Model()

        # Set GUI window size
        self.window_width, self.window_height = 1440, 847
        self.setMinimumSize(round(self.window_width / 2), self.window_height)

        # Pygame graphics renderer
        self.pygame_graphics = PygameGraphics(self.window_width, self.window_height, self.model)

        # Junction view widget
        self.pygame_widget = PyGameWidget(None)
        self.setCentralWidget(self.pygame_widget)
        self.pygame_widget.connect(self.pygame_widget_scroll)
        self.pygame_widget.setFixedWidth(round(self.window_width / 2))

        # Initialise render
        self.render_pygame_widget()

        # GUI refresh timer (set at 100FPS)
        self.timer = Timer(10, self.refresh_pygame_widget, single_shot=False)

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
            draw_grid=True,
            draw_hermite_paths=True,
            draw_nodes=True,
            draw_vehicles=True,
            draw_node_labels=False,
            draw_path_labels=False,
            draw_curvature=False,
            draw_lights=True
        )
        self.pygame_widget.refresh(self.pygame_graphics.surface)

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

    def update_nodes_paths(self, nodes, paths, refresh_widgets=True):
        """

        Updates the list of nodes and paths
        :param nodes: list of nodes
        :param paths: list of paths
        :param refresh_widgets: If nodes are changed on the back-end then the widgets (on the front end) need updating
        :return:
        """
        self.model.nodes = nodes
        self.model.paths = paths
        if refresh_widgets:
            self.design_tab.update_node_path_widgets(self.model.nodes, self.model.paths)
        self.control_tab.set_add_light_button_state()

    def get_data(self) -> tuple:
        """

        :return: Returns the list of nodes and paths
        """
        return self.model.nodes, self.model.paths, self.model.vehicles