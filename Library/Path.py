from Library.Node import Node


class Path:
    def __init__(self, uid: int, start_node: Node, end_mode: Node, fourier_equation: list):
        self.uid = uid
        self.start_node = start_node
        self.end_node = end_mode
        self.fourier_equation = fourier_equation
        self.vehicles = []
