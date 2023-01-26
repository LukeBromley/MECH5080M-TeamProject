from platform import system
import os
from time import sleep
if system() == 'Windows':
    import sys
    sys.path.append('./')

from Frontend.JunctionVisualiser import *

Visualiser = JunctionVisualiser()


def main():
    y = 0
    x = 0
    y_change = 0.01
    x_change = 0.02
    while(True):
        y = y + y_change
        x = x + x_change

        if y > 1:
            y_change = -0.01
            y = 1
        elif y < -1:
            y_change = 0.01
            y = -1

        if x > 1:
            x_change = -0.02
            x = 1
        elif x < -1:
            x_change = 0.02
            x = -1

        sleep(0.01)

        Visualiser.update_car_positions([[x, y]])


Visualiser.define_main(main)
Visualiser.load_junction(os.path.join(os.path.dirname(__file__), "../Frontend/example_junction.junc"))
Visualiser.set_scale(100)
Visualiser.open()
