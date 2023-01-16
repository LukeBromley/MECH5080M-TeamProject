import math
import sympy as sym


class Simulation:
    def __init__(self):
        pass


if __name__ == "__main__":

    # Define the radius
    R = 2

    # Define symbolic variables
    x = sym.Symbol('x')

    # Define the function
    # y = sym.sqrt(R*2 - x**2)
    y = x*2
    print(f"y = {y}")

    # Find the derivative
    first_order_diff = sym.diff(y, x)
    print(f"y' = {first_order_diff}")

    second_order_diff = sym.diff(sym.diff(y, x), x)
    print(f"y'' = {second_order_diff}")

    # Define the distance traveled
    distance_traveled = 1.0

    # Find the coordinates
    x_0 = 0.0
    arc_length_function = sym.integrate(sym.sqrt(1 + sym.diff(y, x)**2), x)
    print(f"Arc length function = {arc_length_function}")

    # Numerical solution
    x_n = sym.nsolve(distance_traveled + arc_length_function.subs(x, x_0).evalf() - arc_length_function, x, 1.0)

    print(f"To solve: {distance_traveled + arc_length_function.subs(x, x_0).evalf() - arc_length_function}")
    y_n = y.subs(x, x_n)

    print(f"x: {x_n}; y: {y_n}")

    # Symbolic solution
    # print(sym.solveset(distance_traveled + arc_length_function.subs(x, x_0).evalf() - arc_length_function, x))

    curvature = abs(second_order_diff.subs(x, x_n)) / math.pow(1 + first_order_diff.subs(x, x_n) ** 2, 3/2)
    print(f"Curvature: {curvature}")
