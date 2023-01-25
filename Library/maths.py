from math import sqrt

class Vector:
    def __init__(self, i: float, j: float, k: float):
        self.i = i
        self.j = j
        self.k = k

def calculate_vector_magnitude(A: Vector):
    return sqrt(A.i**2 + A.j**2 + A.k**2)

def calculate_cross_product(A: Vector, B: Vector):
    return Vector(0, 0, A.i * B.j - A.j * B.i)
