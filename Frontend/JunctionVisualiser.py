import sys
from Tabs.PygameGraphics import *
from Tabs.ControlTab import *
from PyQt5.QtCore import QThread, QObject, pyqtSignal
from Library.FileManagement import *


class JunctionVisualiser:
    def __init__(self) -> None:
        """

        Class the executes the PYQT GUI
        Any code after this class will not be executed until the GUI window is closed.
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

    def load_junction(self, junction_file_path):
        file_manager = FileManagement()
        nodes, paths, lights = file_manager.load_from_junction_file(junction_file_path)
        self.viewer_window.nodes = nodes
        self.viewer_window.paths = paths
        self.viewer_window.render_pygame_widget()

    def define_main(self, function):
        self.worker.set_main_function(function)

    def open(self):
        self.thread.start()
        self.viewer_window.show()
        self.application.exec_()

    def update_car_positions(self, car_positions: list) -> None:
        self.viewer_window.cars = car_positions


class Run_Time_Function(QObject):
    finished = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.function = None

    def run(self):
        self.function()
        self.finished.emit()

    def set_main_function(self, function):
        self.function = function


class ViewerMainWindow(QtWidgets.QMainWindow):
    def __init__(self) -> None:
        """

        Main GUI window.
        Contains all subwidgets
        """
        super(ViewerMainWindow, self).__init__()

        # List of all nodes and paths
        self.nodes = []
        self.paths = []
        self.cars = []

        # Set GUI window size
        self.window_width, self.window_height = 1440, 847
        self.setMinimumSize(round(self.window_width / 2), self.window_height)

        # Pygame graphics renderer
        self.pygame_graphics = PygameGraphics(self.window_width, self.window_height, self.get_nodes_paths)

        # Junction view widget
        self.pygame_widget = PyGameWidget(None)
        self.setCentralWidget(self.pygame_widget)
        self.pygame_widget.connect(self.pygame_widget_scroll)
        self.pygame_widget.setFixedWidth(round(self.window_width / 2))

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
            draw_grid=True,
            draw_hermite_paths=True,
            draw_nodes=True,
            draw_cars=True,
            draw_node_labels=False,
            draw_path_labels=False,
            draw_curvature=False,
        )
        self.pygame_widget.refresh(self.pygame_graphics.surface)

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

    def get_nodes_paths(self) -> tuple:
        """

        :return: Returns the list of nodes and paths
        """
        return self.nodes, self.paths