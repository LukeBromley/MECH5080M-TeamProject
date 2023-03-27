import sys
from .Tabs.pygame_graphics import *
from .Tabs.control_tab import *
from PyQt5.QtCore import QThread, QObject, pyqtSignal
from library.file_management import *
from library.maths import clamp
from library.model import Model


class JunctionVisualiser:
    def __init__(self) -> None:
        """

        Junction Visualiser is a stripped down version of Junction Designer that allows the user to view the junction
        and cars in real time. The window is based on PYQT and uses PyGame for rendering the graphics.
        The application creates a thread that is used to run functions that update the visualiser.

        The visualiser updates at its own independent frame rate (100FPS) using the most recent information provided.

        """
        # Create application
        self.application = QtWidgets.QApplication(sys.argv)
        self.application.setStyle('Windows')  # REQUIRED to show tickable combo boxes!!!!
        # Main window object + display it
        self.viewer_window = ViewerMainWindow()
        # Threading
        self.thread = QThread()
        self.worker = RunTimeFunction()
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

    def load_junction(self, junction_file_path: str) -> None:
        """

        Load the junction into the visualiser for displaying its layout.

        :param junction_file_path: file path of junction (.junc) file to use
        :return: None
        """
        self.viewer_window.model.load_junction(junction_file_path, quick_load=True)
        self.viewer_window.render_pygame_widget()

    def define_main(self, thread_function: classmethod) -> None:
        """

        Specifies the function that should be used to run on the thread
        :param thread_function: function to be run
        :return: None
        """
        self.worker.set_thread_function(thread_function)

    def open(self) -> None:
        """

        Opens Junction Visualiser and start running the thread.

        :return: None
        """
        self.thread.start()
        self.viewer_window.show()
        self.application.exec_()

    def update_vehicle_positions(self, vehicle_data: list) -> None:
        """

        Passes current vehicle data into the visualiser to be saved.
        The visualiser updates at an independent frame rate using most recent vehicle data provided.

        :param vehicle_data: Coordinate locations, size, angle etc of vehicles
        :return: None
        """
        self.viewer_window.model.vehicles = vehicle_data

    def update_light_colours(self, lights: list) -> None:
        """

        Passes current light objects into the visualiser to be saved.
        The visualiser updates at an independent frame rate using most recent lights provided.

        :param lights: list of light objects
        :return: None
        """
        self.viewer_window.model.lights = lights

    def update_time(self, time: Time) -> None:
        """

        Updates the background colour of the visualiser depending on the time of day. White at midday, Black at midnight.
        The visualiser updates at an independent frame rate using most recent time provided.

        :param time: Time object from simulation model
        :return: None
        """
        seconds = time.total_seconds()
        colour_mag = 255 - (255 * abs((seconds - (12 * 60 * 60)) / (12 * 60 * 60)))  # Calculates the background colour
        self.viewer_window.pygame_graphics.background_colour = (colour_mag, colour_mag, colour_mag)

    def update_collision_warning(self, collision: bool) -> None:
        """

        Makes the background colour of the visualiser red if there is currently a crash.
        The visualiser updates at an independent frame rate using most recent background colour.

        :param collision: True if there is a collision.
        :return: None
        """
        if collision:
            self.viewer_window.pygame_graphics.background_colour = (255, 0, 0)

    def update(self, vehicle_data: list = (), lights: list = (), time_of_day: Time = Time(12, 0, 0), collision: bool = False) -> None:
        """

        Updates the visualiser with the current information from the simulation.
        The visualiser updates at an independent frame rate using most recent information provided.

        :param vehicle_data: Current simulation vehicle position, size, direction etc
        :param lights: Current simulation light states
        :param time_of_day: Current simulation time
        :param collision: Current simulation collision states
        :return: None
        """
        self.update_vehicle_positions(vehicle_data)
        self.update_light_colours(lights)
        self.update_time(time_of_day)
        self.update_collision_warning(collision)

    def set_scale(self, scale: int) -> None:
        """

        Changes the GUI scale (percentage) between 10% to 200%.
        :param scale: scale percentage
        :return: None
        """
        scale = clamp(scale, 10, 200)
        scale = 0.2 * scale / 100
        self.viewer_window.pygame_graphics.set_scale(scale)


class RunTimeFunction(QObject):
    # Indicator for the function completing execution
    finished = pyqtSignal()

    def __init__(self):
        """

        QObject inherited class used to store and run the function that is to be run on the thread.

        """
        super().__init__()
        self.thread_function = None

    def run(self) -> None:
        """

        Runs the thread function

        :return: None
        """
        self.thread_function()

    def set_thread_function(self, thread_function: classmethod) -> None:
        """

        Sets the function to run on the second thread.

        :param thread_function: Function to run on second thread.
        :return: None
        """
        self.thread_function = thread_function


class ViewerMainWindow(QtWidgets.QMainWindow):
    def __init__(self) -> None:
        """

        Main GUI window used for junction visualiser. Contains all sub-widgets and visualiser model.

        """
        super(ViewerMainWindow, self).__init__()

        # Visualiser model
        self.model = Model()

        # Set Window size
        self.window_width, self.window_height = 1440, 847
        self.setMinimumSize(round(self.window_width / 2), self.window_height)

        # Pygame graphics renderer class
        self.pygame_graphics = PygameGraphics(self.window_width, self.window_height, self.model)

        # Junction view widget
        self.pygame_widget = PyGameWidget(None)
        self.setCentralWidget(self.pygame_widget)
        self.pygame_widget.connect(self.pygame_widget_scroll)
        self.pygame_widget.setFixedWidth(round(self.window_width / 2))

        # Initialise render
        self.render_pygame_widget()

        # GUI refresh timer (set at 100FPS)
        # This timer loops and when it resets it refreshes the graphics.
        self.timer = Timer(10, self.refresh_pygame_widget, single_shot=False)

    def refresh_pygame_widget(self, force_full_refresh: bool = True) -> None:
        """

        Refreshes the pygame widget with the current graphics rendering. Junction paths are pre-rendered to improve
        performance but simpler elements (like nodes) are rendered on the refresh.

        Vehicle positions changes are rendered on a separate surface to the main surface (that holds the junction
        layout) which means that we can improve performance by only refreshing the vehicle surface. A full refresh
        refreshes everything which is default behavior.

        :param force_full_refresh: Refreshes all surfaces
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

    def update_nodes_paths(self, nodes: list, paths: list, refresh_widgets: bool = True) -> None:
        """

        Updates the list of nodes and paths stored in the model. If nodes are changed on the back-end then the
        widgets (on the front end) need updating.

        :param nodes: list of nodes
        :param paths: list of paths
        :param refresh_widgets: True to refresh all widgets.
        :return:
        """
        self.model.nodes = nodes
        self.model.paths = paths
        if refresh_widgets:
            self.design_tab.update_node_path_widgets(self.model.nodes, self.model.paths)
        self.control_tab.set_add_light_button_state()