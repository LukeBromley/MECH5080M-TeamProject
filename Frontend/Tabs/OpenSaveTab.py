from Frontend.Tabs.PYQTShortcuts import *
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtCore import Qt

from Frontend.JunctionFileManagement import *


class OpenSaveTab(QtWidgets.QWidget):
    def __init__(self, refresh_pygame_widget, render_function, update_nodes_paths_function, get_nodes_paths_function):
        super().__init__()

        self.refresh_pygame_widget = refresh_pygame_widget
        self.render_function = render_function
        self.update_nodes_paths_function = update_nodes_paths_function
        self.get_nodes_paths_function = get_nodes_paths_function

        self.save_file_path = None

        self.v_box = VBox(self, align=Qt.AlignTop)
        self.open = Button(self, "Open Junction", layout=self.v_box)
        self.save = Button(self, "Save Junction", layout=self.v_box)
        self.save.setDisabled(True)
        self.save_as = Button(self, "Save As Junction", layout=self.v_box)
        self.new = Button(self, "New Junction", layout=self.v_box)
        self.new.setDisabled(True)
        self.example = Button(self, "Load Example Junction", layout=self.v_box)

        self.connect()

    def open_junction_with_file_dialog(self):
        file_path = QFileDialog.getOpenFileName(self, 'Open Junction', '.', "Junction Files (*.junc)")[0]
        if len(file_path) > 0:
            self.open_junction(file_path)

    def open_junction(self, file_path):
        self.save_file_path = file_path
        FileManager = JunctionFileManagement()
        nodes, paths = FileManager.load_from_file(self.save_file_path)
        self.update_nodes_paths_function(nodes, paths)
        self.render_function()
        self.save.setEnabled(True)
        self.new.setEnabled(True)

    def save_junction(self):
        if self.save_file_path is not None:
            FileManager = JunctionFileManagement()
            nodes, paths = self.get_nodes_paths_function()
            FileManager.save_to_file(self.save_file_path, nodes, paths)

    def save_as_junction(self):
        file_path = QFileDialog.getSaveFileName(self, 'Save Junction', '.', "Junction Files (*.junc)")[0]
        if len(file_path) > 0:
            self.save_file_path = file_path
            FileManager = JunctionFileManagement()
            nodes, paths = self.get_nodes_paths_function()
            FileManager.save_to_file(self.save_file_path, nodes, paths)
            self.save.setEnabled(True)
            self.new.setEnabled(True)

    def new_junction(self):
        if self.save_file_path is not None:
            self.save_junction()
        self.update_nodes_paths_function([], [])
        self.save_file_path = None
        self.save.setDisabled(True)
        self.new.setDisabled(True)
        self.render_function()

    def load_example(self):
        self.open_junction("example_junction.junc")
        self.save.setDisabled(True)

    def connect(self):
        self.open.pressed.connect(self.open_junction_with_file_dialog)
        self.save.pressed.connect(self.save_junction)
        self.save_as.pressed.connect(self.save_as_junction)
        self.new.pressed.connect(self.new_junction)
        self.example.pressed.connect(self.load_example)

