from math import sin, cos


class Node:
    def __init__(self, uid: int, x: float, y: float, angle):
        self.uid = uid
        self.x = x
        self.y = y
        self.angle = angle

    def get_tangents(self, _weight=None):
        tx = _weight * sin(self.angle)
        ty = -_weight * cos(self.angle)
        return tx, ty



