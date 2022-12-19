import matplotlib.pyplot as plt
from scipy.fft import fft, fftfreq
import numpy as np

'''
Created by Henry Triff
With help from: 
    https://www.cubic.org/docs/hermite.htm
    https://math.vanderbilt.edu/schectex/courses/cubic/

'''


class Point:
    def __init__(self, x, y, tx, ty):
        self.x = x
        self.y = y
        self.tx = tx
        self.ty = ty


# FUNCTIONS
def Plot(p1, p2, x_array, y_array):
    plt.plot(x_array, y_array, color='blue', marker=".")
    plt.plot([p1.x, p1.x + p1.tx * vector_scale], [p1.y, p1.y + p1.ty * vector_scale], color='red', marker=".")
    plt.plot([p2.x, p2.x + p2.tx * vector_scale], [p2.y, p2.y + p2.ty * vector_scale], color='red', marker=".")
    plt.plot([p1.x], [p1.y], color='green', marker="o")
    plt.plot([p2.x], [p2.y], color='green', marker="o")
    # plt.plot(x_array, y_array_fourier.real, color='blue', marker=".")
    plt.show()


def CubeRoot(x):
    if 0 <= x:
        return x**(1./3.)
    return -(-x)**(1./3.)


def CalculateCubeRoots(a, b, c, d):
    p = -b/(3*a)
    q = p**3 + (((b*c)-(3*a*d)) / (6*(a**2)))
    r = c / (3*a)
    return CubeRoot(q + (q**2 + (r-(p**2))**3)**0.5) + CubeRoot(q - (q**2 + (r-(p**2))**3)**0.5) + p


# SETUP
vector_scale = 0.1

p1 = Point(0, 0, 2, 0)
p2 = Point(1, 1, -2, 0)

x_array = []
y_array = []

# # METHOD 1
# # Generate line using Cubic Hermite Curve Interpolation
# for i in range(100):
#     s = i/100
#     h1 = (2 * s**3) - (3 * s**2) + 1
#     h2 = (-2 * s**3) + (3 * s**2)
#     h3 = (s**3) - (2 * s**2) + s
#     h4 = (s**3) - (s**2)
#
#     x_array.append(h1*p1.x + h2*p2.x + h3*p1.tx - h4*p2.tx)
#     y_array.append(h1*p1.y + h2*p2.y + h3*p1.ty - h4*p2.ty)
#
# Plot(p1, p2, x_array, y_array)
#
# # METHOD 2
# # Separate out coefficients for Cubic Hermite Curve Interpolation
# x_array.clear()
# y_array.clear()
# for i in range(100):
#     s = i/100
#     x_array.append(p1.x + p1.tx*(s) + (-3*p1.x+3*p2.x-2*p1.tx+p2.tx)*(s*s) + (2*p1.x-2*p2.x+p1.tx-p2.tx)*(s*s*s))
#     y_array.append(p1.y + p1.ty*(s) + (-3*p1.y+3*p2.y-2*p1.ty+p2.ty)*(s*s) + (2*p1.y-2*p2.y+p1.ty-p2.ty)*(s*s*s))
#
# Plot(p1, p2, x_array, y_array)
#
# # METHOD 3
# # Pre-compute coefficients (more efficient)
# x_array.clear()
# y_array.clear()
# x_coeff = [p1.x, p1.tx, -3*p1.x+3*p2.x-2*p1.tx+p2.tx, 2*p1.x-2*p2.x+p1.tx-p2.tx]
# y_coeff = [p1.y, p1.ty, -3*p1.y+3*p2.y-2*p1.ty+p2.ty, 2*p1.y-2*p2.y+p1.ty-p2.ty]
# for i in range(100):
#     s = i/100
#     x_array.append(x_coeff[0] + x_coeff[1]*s + x_coeff[2]*(s*s) + x_coeff[3]*(s*s*s))
#     y_array.append(y_coeff[0] + y_coeff[1]*s + y_coeff[2]*(s*s) + y_coeff[3]*(s*s*s))
#
# Plot(p1, p2, x_array, y_array)
#
# # METHOD 4
# # Convert from s-based lines to x-y coordinates
# # This has the limitation that you cannot generate lines that have two y points for each x point
# x_array.clear()
# y_array.clear()
# x_coeff = [p1.x, p1.tx, -3*p1.x+3*p2.x-2*p1.tx+p2.tx, 2*p1.x-2*p2.x+p1.tx-p2.tx]
# y_coeff = [p1.y, p1.ty, -3*p1.y+3*p2.y-2*p1.ty+p2.ty, 2*p1.y-2*p2.y+p1.ty-p2.ty]
# for i in range(100):
#     x = i/100
#     x_array.append(x)
#     s = CalculateCubeRoots(x_coeff[3], x_coeff[2], x_coeff[1], x_coeff[0] - x)
#     y_array.append(y_coeff[0] + y_coeff[1] * s + y_coeff[2] * (s * s) + y_coeff[3] * (s * s * s))
# # Apply FFT to get coefficients
# fourier_coefficients = np.fft.fft(y_array, n=10)
#
# # Use coefficients to regenerate spline
# y_array_fourier = np.fft.ifft(fourier_coefficients)
#
# Plot(p1, p2, x_array, y_array_fourier)

# METHOD 5
# Pre-compute coefficients (more efficient)
# x_array.clear()
# y_array.clear()
# x_coeff = [p1.x, p1.tx, -3*p1.x+3*p2.x-2*p1.tx+p2.tx, 2*p1.x-2*p2.x+p1.tx-p2.tx]
# y_coeff = [p1.y, p1.ty, -3*p1.y+3*p2.y-2*p1.ty+p2.ty, 2*p1.y-2*p2.y+p1.ty-p2.ty]
# for i in range(100):
#     s = i/100
#     x_array.append(x_coeff[0] + x_coeff[1]*s + x_coeff[2]*(s*s) + x_coeff[3]*(s*s*s))
#     y_array.append(y_coeff[0] + y_coeff[1]*s + y_coeff[2]*(s*s) + y_coeff[3]*(s*s*s))

# for i in range(99):
#     dx = x_array[i+1] - x_array[i]
#     dy = y_array[i+1] - y_array[i]
#     length = (dx*dx + dy*dy)**0.5
#     print(str(dx) + ", ", str(dy) + ", " + str(length))
#
# plt.plot(x_array, y_array, color='blue')
# plt.plot([p1.x, p1.x + p1.tx * vector_scale], [p1.y, p1.y + p1.ty * vector_scale], color='red', marker=".")
# plt.plot([p2.x, p2.x + p2.tx * vector_scale], [p2.y, p2.y + p2.ty * vector_scale], color='red', marker=".")
# plt.plot([p1.x], [p1.y], color='green', marker="o")
# plt.plot([p2.x], [p2.y], color='green', marker="o")
#
# for i in range(10):
#     x = i/10
#     s = CalculateCubeRoots(x_coeff[3], x_coeff[2], x_coeff[1], x_coeff[0] - x)
#     plt.plot(x, (y_coeff[0] + y_coeff[1] * s + y_coeff[2] * (s * s) + y_coeff[3] * (s * s * s)), color='Green', marker=".")
#
# plt.show()

# METHOD 6
# Fitting a polynomial to the line
x_array.clear()
y_array.clear()
x_coeff = [p1.x, p1.tx, -3*p1.x+3*p2.x-2*p1.tx+p2.tx, 2*p1.x-2*p2.x+p1.tx-p2.tx]
y_coeff = [p1.y, p1.ty, -3*p1.y+3*p2.y-2*p1.ty+p2.ty, 2*p1.y-2*p2.y+p1.ty-p2.ty]
for i in range(101):
    s = i/100
    x_array.append(x_coeff[0] + x_coeff[1]*s + x_coeff[2]*(s*s) + x_coeff[3]*(s*s*s))
    y_array.append(y_coeff[0] + y_coeff[1]*s + y_coeff[2]*(s*s) + y_coeff[3]*(s*s*s))


n_max = 20
polynomial = np.polyfit(x_array, y_array, n_max)
coefs = list(polynomial)

x_poly_array = []
y_poly_array = []
for i in range(101):
    x = i/100
    x_poly_array.append(x)
    y = 0
    for n, coef in enumerate(coefs):
        y += coef * pow(x, n_max - n)
    y_poly_array.append(y)

# plt.plot(x_array, y_array, color='blue')
plt.plot(x_poly_array, y_poly_array, color='blue')
plt.plot([p1.x, p1.x + p1.tx * vector_scale], [p1.y, p1.y + p1.ty * vector_scale], color='red', marker=".")
plt.plot([p2.x, p2.x + p2.tx * vector_scale], [p2.y, p2.y + p2.ty * vector_scale], color='red', marker=".")
plt.plot([p1.x], [p1.y], color='green', marker="o")
plt.plot([p2.x], [p2.y], color='green', marker="o")
plt.show()
