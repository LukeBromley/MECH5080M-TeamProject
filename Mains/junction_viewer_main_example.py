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
    x = 50
    y_change = 1
    x_change = 2
    while(True):
        y = y + y_change
        x = x + x_change

        if y > 100:
            y_change = -1
            y = 100
        elif y < -100:
            y_change = 1
            y = -100

        if x > 100:
            x_change = -2
            x = 100
        elif x < -100:
            x_change = 2
            x = -100

        sleep(0.01)

        Visualiser.update_car_positions([[x, y]])


Visualiser.define_main(main)
Visualiser.load_junction(os.path.join(os.path.dirname(__file__), "../Frontend/example_junction.junc"))
Visualiser.set_scale(100)
Visualiser.open()
