import random

LANES = ["A", "B", "C"]
MINIMUM_START_VELOCITY = 1
MAXMUM_START_VELOCITY = 8
MINIMUM_START_ACCELERATION = -1
MAXIMUM_START_ACCELERATION = 1
MIN_LENGTH = 2
MAX_LENGTH = 5
MIN_WIDTH = 1
MAX_WIDTH = 2

TICK = 0.1

MAX_CARS = 4

VEHICLE_WIDTH_MIN_MAX = [1.6, 2.1]  # AVG = 1.82
VEHICLE_LENGTH_MIN_MAX = [3.4, 5.0]  # AVG = 4.40

for i in range(100):
    width = random.gauss(1.813, 0.116)
    length = random.gauss(4.542, 0.579)
    print(width, length)
