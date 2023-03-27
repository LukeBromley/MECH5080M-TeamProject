from gui.Tabs.pyqt_shortcuts import *
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtCore import Qt
import os

from library.file_management import *


class OpenSaveTab(QtWidgets.QWidget):
    def __init__(self, gui, model):
        """

        OpenSave tab that allows the user to add open and save a junction to file. Also allows a new junction to be made
        and to open an example junction.

        :param gui: parent gui class
        :param model: model
        """
        super().__init__()

        # Parent GUI and parent model
        self.model = model
        self.gui = gui

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

        Opens the open file dialog box and gets desired file path + file name. If a file has been specified then the
        junction will be loaded into the model. The save_file_path will be updated for easier saving in the future.

        :return: None
        """
        file_path = QFileDialog.getOpenFileName(self, 'Open Junction', '../junctions', "Junction Files (*.junc)")[0]
        if len(file_path) > 0:
            self.open_junction(file_path)

    def open_junction(self, file_path: str) -> None:
        """

        Loads the junction into the model, renders the viewer and updates all tabs.

        :param file_path: file path of the junction (.junc) file that is loaded.
        :return: None
        """
        self.save_file_path = file_path

        self.model.load_junction(self.save_file_path, quick_load=True)
        self.gui.render_pygame_widget()
        self.gui.update_design_tab()
        self.gui.update_control_tab()
        self.save.setEnabled(True)
        self.new.setEnabled(True)

    def save_junction(self) -> None:
        """

        Saves the junction if the save location has already been specified. A save location is specified when opening
        a .junc file or after save-as-ing a .junc file. The file saved will be a .junc file.

        :return: None
        """
        if self.save_file_path is not None:
            self.model.save_junction(self.save_file_path)

    def save_as_junction(self) -> None:
        """

        Opens the open file dialog box and gets desired file path + file name. If a file has been specified then the
        junction will be saved as a .junc file. The save_file_path will be updated for easier saving in the future.

        :return: None
        """
        path = os.path.join(os.path.dirname(__file__), ".../junctions")
        file_path = QFileDialog.getSaveFileName(self, 'Save Junction', path, "Junction Files (*.junc)")[0]
        if len(file_path) > 0:
            self.save_file_path = file_path
            self.model.save_junction(self.save_file_path)
            self.save.setEnabled(True)
            self.new.setEnabled(True)

    def new_junction(self) -> None:
        """

        Creates a new junction with zero nodes and zero paths.

        :return: None
        """
        if self.save_file_path is not None:
            self.save_junction()
        self.gui.update_nodes_paths_function([], [])
        self.save_file_path = None
        self.save.setDisabled(True)
        self.new.setDisabled(True)
        self.gui.render_function()

    def load_example(self) -> None:
        """

        Opens and loads the example junction.

        :return: None
        """

        self.open_junction(os.path.join(os.path.dirname(__file__), "../example_junction.junc"))
        self.save.setDisabled(True)

    def connect(self) -> None:
        """

        Connects the buttons in the save menu to the relevant callback functions.

        :return: None
        """
        self.open.pressed.connect(self.open_junction_with_file_dialog)
        self.save.pressed.connect(self.save_junction)
        self.save_as.pressed.connect(self.save_as_junction)
        self.new.pressed.connect(self.new_junction)
        self.example.pressed.connect(self.load_example)

