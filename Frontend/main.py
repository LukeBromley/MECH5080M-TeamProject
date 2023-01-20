import sys
sys.path.append('./')
from JunctionVisualiser import *


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

        ans = (2 / 3) * pow(u, (3 / 2)) * (1 / du)

        llist.append(ans)

    L = llist[0] - llist[1]
    return L


# Main function
def main() -> None:
    """

    Main function to test and run the junction visualiser
    :return: None
    """
    Visualiser = JunctionVisualiser()


if __name__ == "__main__":
    main()
