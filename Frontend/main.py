import sys
sys.path.append("..")
from JunctionVisualiser import *
from Library.infrastructure import Node
from Library.infrastructure import Path
from math import pi, sqrt
import sympy

# List of nodes
nodes = [
    Node(0, -200, -200, pi/2),
    Node(1, 200, 200, pi),
    Node(2, 100, -200),
    Node(3, 200, -100),
]


# Calculating coefficients for spline lines
def calculate_quadratic_bezier(start_node, mid_node, end_node):
    p0_x = start_node.x
    p1_x = mid_node.x
    p2_x = end_node.x

    p0_y = start_node.y
    p1_y = mid_node.y
    p2_y = end_node.y

    _x_coeff = [p0_x, -2 * (p0_x - p1_x), (p0_x + p2_x - 2*p1_x)]
    _y_coeff = [p0_y, -2 * (p0_y - p1_y), (p0_y + p2_y - 2*p1_y)]

    return _x_coeff, _y_coeff


def calculate_cubic_bezier(start_node, mid_node_1, mid_node_2, end_node):
    p0_x = start_node.x
    p1_x = mid_node_1.x
    p2_x = mid_node_2.x
    p3_x = end_node.x

    _x_coeff = [p0_x, (3*p1_x - 3*p0_x), (3*p0_x - 6*p1_x + 3*p2_x), (-p0_x + 3*p1_x - 3*p2_x + p3_x)]

    p0_y = start_node.y
    p1_y = mid_node_1.y
    p2_y = mid_node_2.y
    p3_y = end_node.y

    _y_coeff = [p0_y, (3*p1_y - 3*p0_y), (3*p0_y - 6*p1_y + 3*p2_y), (-p0_y + 3*p1_y - 3*p2_y + p3_y)]

    return _x_coeff, _y_coeff



# List of paths
paths = [
    Path(1, nodes[0], nodes[1], calculate_cubic_bezier(nodes[0], nodes[2], nodes[3], nodes[1])),
]


# Find length along spline
def find_length(path):

    # https://math.libretexts.org/Bookshelves/Calculus/Book%3A_Calculus_(OpenStax)/11%3A_Parametric_Equations_and_Polar_Coordinates/11.02%3A_Calculus_of_Parametric_Curves#:~:text=The%20arc%20length%20of%20a%20parametric%20curve%20can%20be%20calculated,dt)2dt.

    a = path.x_coeff[1]
    b = path.x_coeff[2]
    c = path.x_coeff[3]
    d = path.y_coeff[1]
    e = path.y_coeff[2]
    f = path.y_coeff[3]

    slist = [1, 0]

    llist = []

    for s in slist:
        u1 = pow(a, 2)
        u2 = 4 * pow(b, 2) * pow(s, 2)
        u3 = 9 * pow(c, 2) * pow(s, 4)
        u4 = 4 * a * b * s
        u5 = 6 * a * c * pow(s, 2)
        u6 = 12 * b * c * pow(s, 3)
        u7 = pow(d, 2)
        u8 = 4 * pow(e, 2) + pow(s, 2)
        u9 = 9 * pow(f, 2) + pow(s, 4)
        u10 = 4 * d * e * s
        u11 = 6 * d * f * pow(s, 2)
        u12 = 12 * e * f * pow(s, 3)

        u = u1 + u2 + u3 + u4 + u5 + u6 + u7 + u8 + u9 + u10 + u11 + u12

        du1 = 8 * pow(b, 2) * s
        du2 = 36 * pow(c, 2) * pow(s, 3)
        du3 = 4 * a * b
        du4 = 12 * a * c * s
        du5 = 36 * b * c * pow(s, 2)
        du6 = 8 * pow(e, 2) * s
        du7 = 36 * pow(f, 2) * pow(s, 3)
        du8 = 4 * d * e
        du9 = 12 * d * f * s
        du10 = 36 * e * f * pow(s, 2)

        du = du1 + du2 + du3 + du4 + du5 + du6 + du7 + du8 + du9 + du10

        ans = (2/3) * pow(u, (3/2)) * (1 / du)

        llist.append(ans)

    L = llist[0] - llist[1]
    return L


# Main function
def main():
    Visualiser = JunctionVisualiser()
    while True:
        Visualiser.refresh()
        Visualiser.draw_bezian_cubic_paths(paths)
        Visualiser.draw_nodes(nodes)
        Visualiser.update()


if __name__ == "__main__":
    main()