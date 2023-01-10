import sys

from Tabs.PygameGraphics import *
from Tabs.OpenSaveTab import *
from Tabs.DesignTab import *
from Tabs.ViewTab import *


class JunctionVisualiser:
    def __init__(self):

        self.application = QtWidgets.QApplication(sys.argv)
        self.main_window = MainWindow()
        self.main_window.show()
        self.application.exec_()


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.nodes = []
        self.paths = []

        self.setMinimumSize(1280, 720)

        self.main_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.main_widget)

        self.h_box = HBox(self.main_widget)

        self.pygame_graphics = PygameGraphics(self.get_nodes_paths)
        self.pygame_widget = PyGameWidget(self.main_widget, layout=self.h_box)
        self.pygame_widget.connect(self.pygame_widget_scroll)
        self.pygame_widget.setFixedWidth(640)

        self.tabs = Tabs(self.main_widget, layout=self.h_box)

        self.open_save_tab = OpenSaveTab(self.refresh_pygame_widget, self.render_pygame_widget, self.update_nodes_paths, self.get_nodes_paths)
        self.tabs.addTab(self.open_save_tab, "Open / Save")

        self.design_tab = DesignTab(self.refresh_pygame_widget, self.render_pygame_widget, self.update_nodes_paths, self.get_nodes_paths)
        self.tabs.addTab(self.design_tab, "Design")

        self.view_tab = ViewTab(self.refresh_pygame_widget, self.render_pygame_widget, self.recenter)
        self.tabs.addTab(self.view_tab, "View")

        self.render_pygame_widget()

    def refresh_pygame_widget(self):
        self.pygame_graphics.scale = self.view_tab.scale_perc
        self.pygame_graphics.refresh(
            _draw_grid=self.view_tab.show_layer_grid,
            _draw_hermite_paths=self.view_tab.show_layer_hermite_paths,
            _draw_poly_paths=self.view_tab.show_layer_poly_paths,
            _draw_nodes=self.view_tab.show_layer_nodes,
            _draw_node_labels=True if self.view_tab.show_layer_labels and self.view_tab.show_layer_nodes else False,
            _draw_path_labels=True if self.view_tab.show_layer_labels and (self.view_tab.show_layer_hermite_paths or self.view_tab.show_layer_poly_paths) else False,
            _draw_curvature=self.view_tab.show_layer_curvature,
        )
        self.pygame_widget.refresh(self.pygame_graphics.surface)
        x, y = self.pygame_graphics.get_click_position()
        self.design_tab.coords.setText("Mouse Coords: (" + str(x) + ", " + str(y) + ")")

    def render_pygame_widget(self):
        for path in self.paths:
            path.recalculate_coefs()

        if len(self.paths) > 0:
            self.pygame_graphics.render_hermite_paths(self.paths)
            self.pygame_graphics.render_poly_paths(self.paths)
        self.refresh_pygame_widget()

    def pygame_widget_scroll(self, event):
        self.pygame_graphics.calculate_scroll(event)
        self.refresh_pygame_widget()

    def update_nodes_paths(self, nodes, paths, refresh_widgets=True):
        self.nodes = nodes
        self.paths = paths
        if refresh_widgets:
            self.design_tab.update_node_path_widgets(self.nodes, self.paths)

    def get_nodes_paths(self):
        return self.nodes, self.paths

    def recenter(self):
        self.pygame_graphics.recenter()
        self.refresh_pygame_widget()

