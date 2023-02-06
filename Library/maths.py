import math
from math import sqrt, pi, sin, cos
from typing import Union


class Vector:
    def __init__(self, i: float, j: float, k: float):
        self.i = i
        self.j = j
        self.k = k


class VisualPoint:
    def __init__(self, x: int, y: int, colour: tuple) -> None:
        """

        :param x: x coordinate of plotted point
        :param y: y coordinate of plotted point
        :param colour: colour of plotted point
        """
        self.x = x
        self.y = y
        self.colour = colour


def calculate_vector_magnitude(A: Vector):
    return sqrt(A.i**2 + A.j**2 + A.k**2)


def calculate_cross_product(A: Vector, B: Vector):
    return Vector(0, 0, A.i * B.j - A.j * B.i)


def clamp(n: Union[int, float], minn: Union[int, float], maxn: Union[int, float]) -> Union[int, float]:
    """

    Limit a value, n, between minimum and maximum
    :param n: value to be limited
    :param minn: min that n can be
    :param maxn: max that n can be
    :return: limited value
    """
    return max(min(maxn, n), minn)


def calculate_rectangle_corner_coords(x, y, angle, length, width):
    l_2 = length / 2
    w_2 = width / 2

    x0 = l_2 * cos(angle)
    y0 = l_2 * sin(angle)

    x1 = x0 - w_2 * cos(pi / 2 - angle)
    y1 = y0 + w_2 * sin(pi / 2 - angle)

    x2 = x0 + w_2 * cos(pi / 2 - angle)
    y2 = y0 - w_2 * sin(pi / 2 - angle)

    return [(x + x1, y + y1), (x + x2, y + y2), (x - x1, y - y1), (x - x2, y - y2)]


def calculate_line_gradient_and_constant(x1, y1, x2, y2):
    if x2 - x1 != 0:
        m = (y2 - y1) / (x2 - x1)
    else:
        m = math.inf
    c = y1 - m * x1
    return m, c


def calculate_range_overlap(min_a, max_a, min_b, max_b):
    if min_a >= min_b and max_a <= max_b:
        # a:     *----------*
        # b: *------------------*
        return min_a, max_a
    elif min_b >= min_a and max_b <= max_a:
        # a: *------------------*
        # b:     *----------*
        return min_b, max_b
    elif min_b <= min_a <= max_b:
        # a:     *---------------*
        # b: *----------*
        return min_a, max_b
    elif min_b <= max_a <= max_b:
        # a: *----------*
        # b:     *---------------*
        return max_a, min_b
    else:
        return None
