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
    a = 0
    y_change = 0.1
    x_change = 0.2
    a_change = 1
    while(True):
        y = y + y_change
        x = x + x_change
        a = a + a_change

        if y > 6:
            y_change = -0.1
            y = 6
            a_change = 1
        elif y < -2:
            y_change = 0.1
            y = -2
            a_change = -1

        if x > 5:
            x_change = -0.2
            x = 5
            a_change = 2
        elif x < -5:
            x_change = 0.2
            x = -5
            a_change = -2

        sleep(0.01)

        Visualiser.update_car_positions([[x, y, a]])


Visualiser.define_main(main)
Visualiser.load_junction(os.path.join(os.path.dirname(__file__), "../Frontend/example_junction.junc"))
Visualiser.set_scale(200)
Visualiser.open()
