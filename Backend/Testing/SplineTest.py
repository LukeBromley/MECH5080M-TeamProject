import matplotlib.pyplot as plt

'''
Created by Henry Triff
With help from: https://www.cubic.org/docs/hermite.htm

'''


class Point:
    def __init__(self, x, y, tx, ty):
        self.x = x
        self.y = y
        self.tx = tx
        self.ty = ty


vector_scale = 0.1

p1 = Point(0, 0, 3, 0)
p2 = Point(1, 1, -3, 0)

x_array = []
y_array = []
for i in range(100):
    s = i/100
    h1 = (2 * s**3) - (3 * s**2) + 1
    h2 = (-2 * s**3) + (3 * s**2)
    h3 = (s**3) - (2 * s**2) + s
    h4 = (s**3) - (s**2)

    x_array.append(h1*p1.x + h2*p2.x + h3*p1.tx - h4*p2.tx)
    y_array.append(h1*p1.y + h2*p2.y + h3*p1.ty - h4*p2.ty)

plt.plot(x_array, y_array)
plt.plot([p1.x, p1.x + p1.tx * vector_scale], [p1.y, p1.y + p1.ty * vector_scale], color='red', marker=".")
plt.plot([p2.x, p2.x + p2.tx * vector_scale], [p2.y, p2.y + p2.ty * vector_scale], color='red', marker=".")
plt.plot([p1.x], [p1.y], color='green', marker="o")
plt.plot([p2.x], [p2.y], color='green', marker="o")
plt.show()
