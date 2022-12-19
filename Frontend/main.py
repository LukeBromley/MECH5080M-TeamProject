import sys
sys.path.append("..")
from JunctionVisualiser import *
from Library.infrastructure import Node
from Library.infrastructure import Path
from math import pi, sqrt

# List of nodes
nodes = [
    Node(0, -200, -200, pi/2),
    Node(1, -200, -100, pi/2),
    Node(2, -200, 0, -pi/2),

    Node(3, 200, -200, pi/2),
    Node(4, 200, -100, -pi/2),
    Node(5, 200, 0, -pi/2),

    Node(6, -100, 100, 0),
    Node(7, 0, 100, 0),
    Node(8, 100, 100, -pi),

    Node(9, -400, -200, pi/2),
    Node(10, -400, 0, -pi/2),

    Node(11, 400, -200, pi/2),
    Node(12, 400, 0, -pi/2),

    Node(13, -100, 300, 0),
    Node(14, 100, 300, pi),
]

# Calculating coefficients for spline lines
def calculate_line_coefficients(start_node, end_node):
    l = sqrt((start_node.x - end_node.x)**2 + (start_node.y - end_node.y)**2)

    _p1x = start_node.x
    _p1y = start_node.y
    _p1tx, _p1ty = start_node.get_tangents(l*1.5)
    _p2x = end_node.x
    _p2y = end_node.y
    _p2tx, _p2ty = end_node.get_tangents(l*1.5)
    _p2tx = -_p2tx
    _p2ty = -_p2ty

    _x_coeff = [_p1x, _p1tx, -3 * _p1x + 3 * _p2x - 2 * _p1tx + _p2tx, 2 * _p1x - 2 * _p2x + _p1tx - _p2tx]
    _y_coeff = [_p1y, _p1ty, -3 * _p1y + 3 * _p2y - 2 * _p1ty + _p2ty, 2 * _p1y - 2 * _p2y + _p1ty - _p2ty]

    return _x_coeff, _y_coeff

# List of paths
paths = [
    Path(1, nodes[0], nodes[3], calculate_line_coefficients(nodes[0], nodes[3])),
    Path(1, nodes[1], nodes[8], calculate_line_coefficients(nodes[1], nodes[8])),
    Path(1, nodes[4], nodes[2], calculate_line_coefficients(nodes[4], nodes[2])),
    Path(1, nodes[5], nodes[8], calculate_line_coefficients(nodes[5], nodes[8])),
    Path(1, nodes[7], nodes[3], calculate_line_coefficients(nodes[7], nodes[3])),
    Path(1, nodes[6], nodes[2], calculate_line_coefficients(nodes[6], nodes[2])),

    Path(1, nodes[9], nodes[0], calculate_line_coefficients(nodes[9], nodes[0])),
    Path(1, nodes[9], nodes[1], calculate_line_coefficients(nodes[9], nodes[1])),
    Path(1, nodes[2], nodes[10], calculate_line_coefficients(nodes[2], nodes[10])),

    Path(1, nodes[3], nodes[11], calculate_line_coefficients(nodes[3], nodes[11])),
    Path(1, nodes[12], nodes[4], calculate_line_coefficients(nodes[12], nodes[4])),
    Path(1, nodes[12], nodes[5], calculate_line_coefficients(nodes[12], nodes[5])),

    Path(1, nodes[8], nodes[14], calculate_line_coefficients(nodes[8], nodes[14])),
    Path(1, nodes[13], nodes[6], calculate_line_coefficients(nodes[13], nodes[6])),
    Path(1, nodes[13], nodes[7], calculate_line_coefficients(nodes[13], nodes[7])),

]

# Find length along spline
def find_length(path):
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

        llist.append(pow(u, (3/2)) * (1 / du))

    L = llist[0] - llist[1]
    return L


# Main function
def main():
    Visualiser = JunctionVisualiser()
    while True:
        Visualiser.refresh()
        Visualiser.draw_paths(paths)
        Visualiser.draw_nodes(nodes)
        Visualiser.update()


if __name__ == "__main__":
    main()