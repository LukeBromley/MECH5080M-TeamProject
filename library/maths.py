import math
from math import sqrt, pi, sin, cos
from typing import Union


class VisualPoint:
    def __init__(self, x: int, y: int, colour: tuple) -> None:
        """
        Struct like class that represents a coloured point in 2D space.

        :param x: x coordinate of plotted point
        :param y: y coordinate of plotted point
        :param colour: colour of plotted point
        """
        self.x = x
        self.y = y
        self.colour = colour

class Vector:
    def __init__(self, i: float, j: float, k: float):
        """
        Struct like class that is used to represent a vector

        :param i: i direction magnitude
        :param j: k direction magnitude
        :param k: k direction magnitude
        """
        self.i = i
        self.j = j
        self.k = k

def calculate_vector_magnitude(vector: Vector) -> float:
    """
    The calculate_vector_magnitude function calculates the magnitude of a vector.

    :param vector: Vector: Vector that the magnitude needs to be calculated from
    :return: The magnitude of the vector
    """
    return sqrt(vector.i**2 + vector.j**2 + vector.k**2)


def calculate_cross_product(vector_1: Vector, vector_2: Vector) -> Vector:
    """
    The calculate_cross_product function takes two vectors as input and returns the cross product of those two vectors.

    :param vector_1: Vector: Specify the type of the first parameter
    :param vector_2: Vector: Specify that the second parameter is a vector
    :return: Vector objectthat is perpendicular to the two vectors passed as arguments
    """
    return Vector(0, 0, vector_1.i * vector_2.j - vector_1.j * vector_2.i)


def calculate_magnitude(vector_1: float, vector_2: float) -> float:
    """
    The calculate_magnitude function calculates the magnitude of two perpendicular vectors.

    :param vector_1: magnitude of one vector
    :param vector_2: magnitude of another vector
    :return: The magnitude of a vector
    """
    return sqrt(vector_1**2 + vector_2**2)


def clamp(n: Union[int, float], min_n: Union[int, float], max_n: Union[int, float]) -> Union[int, float]:
    """
    Limits the provided value, n, between minimum and maximum

    :param n: value to be limited
    :param min_n: min that n can be
    :param max_n: max that n can be
    :return: limited value
    """
    return max(min(max_n, n), min_n)


def calculate_rectangle_corner_coords(x: Union[int, float], y: Union[int, float], angle: Union[int, float], length: Union[int, float], width: Union[int, float]) -> list:
    """
    The calculate_rectangle_corner_coords function takes in the x and y coordinates of a rectangle's center,
    the angle of rotation, the length and width of the rectangle. It returns a list containing tuples with
    the x and y coordinates for each corner.

    :param x: Set the x coordinate of the center point of the rectangle
    :param y: Set the y coordinate of the rectangle
    :param angle: Determine the angle of the rectangle
    :param length: Determine the length of the rectangle
    :param width: Determine the width of the rectangle
    :return: A list of the four corners
    """
    l_2 = length / 2
    w_2 = width / 2

    x0 = l_2 * cos(angle)
    y0 = l_2 * sin(angle)

    x1 = x0 - w_2 * cos(pi / 2 - angle)
    y1 = y0 + w_2 * sin(pi / 2 - angle)

    x2 = x0 + w_2 * cos(pi / 2 - angle)
    y2 = y0 - w_2 * sin(pi / 2 - angle)

    return [(x + x1, y + y1), (x + x2, y + y2), (x - x1, y - y1), (x - x2, y - y2)]


def calculate_line_gradient_and_constant(x1: Union[int, float], y1: Union[int, float], x2: Union[int, float], y2: Union[int, float]):
    """
    The calculate_line_gradient_and_constant function takes in two points (x,y) and returns the gradient of the line
    between them as well as the y intercept constant.

    :param x1: Represent the x coordinate of one point on the line
    :param y1: Calculate the gradient of the line
    :param x2: Calculate the gradient of the line
    :param y2: Calculate the gradient of the line
    :return: A tuple of the gradient and constant values for a line
    """
    if x2 - x1 != 0:
        m = (y2 - y1) / (x2 - x1)
    else:
        m = math.inf
    c = y1 - m * x1
    return m, c


def calculate_range_overlap(min_a: Union[int, float], max_a: Union[int, float], min_b: Union[int, float], max_b: Union[int, float]):
    """
    The calculate_range_overlap function takes two ranges and returns the overlap between them.

    :param min_a: Represent the minimum value of range a
    :param max_a: Store the maximum value of a
    :param min_b: Represent the minimum value of the second range
    :param max_b: Set the maximum value of b
    :return: None if there is no overlap else provides the range of the overlap
    """
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
