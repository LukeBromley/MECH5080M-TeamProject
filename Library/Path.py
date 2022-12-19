from Library.Node import Node


class Path:
    def __init__(self, uid: int, start_node: Node, end_mode: Node, coeffs: tuple):
        self.uid = uid
        self.start_node = start_node
        self.end_node = end_mode
        self.vehicles = []
        self.x_coeff, self.y_coeff = coeffs[0], coeffs[1]
