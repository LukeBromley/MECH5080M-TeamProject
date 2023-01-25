from Frontend.Tabs.PYQTShortcuts import *
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtCore import Qt

from Library.FileManagement import *


class OpenSaveTab(QtWidgets.QWidget):
    def __init__(self, refresh_pygame_widget, render_function, update_nodes_paths_function, get_nodes_paths_function, update_lights_function, get_lights_function) -> None:
        """

        :param refresh_pygame_widget: function that refreshes the pygame graphics
        :param render_function: function that renders the pygame graphics
        :param update_nodes_paths_function: function that updates the nodes and paths in the top level class
        :param get_nodes_paths_function: function gets nodes and paths from the top level class
        """
        super().__init__()

        # Functions
        self.refresh_pygame_widget = refresh_pygame_widget
        self.render_function = render_function
        self.update_nodes_paths_function = update_nodes_paths_function
        self.get_nodes_paths_function = get_nodes_paths_function
        self.update_lights_function = update_lights_function
        self.get_lights_function = get_lights_function

        # File path
        self.save_file_path = None

        # Widgets + Layouts
        self.v_box = VBox(self, align=Qt.AlignTop)
        self.open = Button(self, "Open Junction", layout=self.v_box)
        self.save = Button(self, "Save Junction", layout=self.v_box)
        self.save.setDisabled(True)
        self.save_as = Button(self, "Save As Junction", layout=self.v_box)
        self.new = Button(self, "New Junction", layout=self.v_box)
        self.new.setDisabled(True)
        self.example = Button(self, "Load Example Junction", layout=self.v_box)

        # Connect buttons
        self.connect()

    def open_junction_with_file_dialog(self) -> None:
        """

        Opens the open file dialog box and gets desired file path + file name
        :return: None
        """
        file_path = QFileDialog.getOpenFileName(self, 'Open Junction', '../Junction_Designs', "Junction Files (*.junc)")[0]
        if len(file_path) > 0:
            self.open_junction(file_path)

    def open_junction(self, file_path: str) -> None:
        """

        :param file_path: file path to save file to
        :return: None
        """
        self.save_file_path = file_path
        FileManager = FileManagement()
        nodes, paths, lights = FileManager.load_from_junction_file(self.save_file_path)
        self.update_nodes_paths_function(nodes, paths)
        self.update_lights_function(lights)
        self.render_function()
        self.save.setEnabled(True)
        self.new.setEnabled(True)

    def save_junction(self) -> None:
        """

        Saves junction if a file path has already been specified
        :return: None
        """
        if self.save_file_path is not None:
            FileManager = FileManagement()
            nodes, paths = self.get_nodes_paths_function()
            lights = self.get_lights_function()
            FileManager.save_to_junction_file(self.save_file_path, nodes, paths, lights)

    def save_as_junction(self) -> None:
        """

        Opens the file dialog box and gets desired file path + file name to save the file to.
        :return: None
        """
        file_path = QFileDialog.getSaveFileName(self, 'Save Junction', '.', "Junction Files (*.junc)")[0]
        if len(file_path) > 0:
            self.save_file_path = file_path
            FileManager = FileManagement()
            nodes, paths = self.get_nodes_paths_function()
            lights = self.get_lights_function()
            FileManager.save_to_junction_file(self.save_file_path, nodes, paths, lights)
            self.save.setEnabled(True)
            self.new.setEnabled(True)

    def new_junction(self) -> None:
        """

        Creates a new junction with zero nodes and zero paths.
        :return: None
        """
        if self.save_file_path is not None:
            self.save_junction()
        self.update_nodes_paths_function([], [])
        self.save_file_path = None
        self.save.setDisabled(True)
        self.new.setDisabled(True)
        self.render_function()

    def load_example(self) -> None:
        """

        Opens the example junction
        :return: None
        """
        self.open_junction("example_junction.junc")
        self.save.setDisabled(True)

    def connect(self) -> None:
        """

        Connects the buttons in the menu with the relevant callback functions
        :return: None
        """
        self.open.pressed.connect(self.open_junction_with_file_dialog)
        self.save.pressed.connect(self.save_junction)
        self.save_as.pressed.connect(self.save_as_junction)
        self.new.pressed.connect(self.new_junction)
        self.example.pressed.connect(self.load_example)

