import matplotlib.pyplot as plt
from math import *

x_array = []
y_array = []

d = 3.65*2
f = 2400000000
c = 300000000
l = c/f

for angle in range(100000):
    t = (angle * 0.1 * pi/100000) - (0.1 * pi/2)
    x_array.append(t * 2 * pi)
    delta = (pi * d * sin(t))/l
    if delta != 0:
        i = ((sin(delta))**2) / delta**2
    else:
        i = 1
    y_array.append(i * 100)

plt.plot(x_array, y_array, color='blue')
plt.xlabel("Angle (°)")
plt.ylabel("Intensity (%)")
plt.show()
