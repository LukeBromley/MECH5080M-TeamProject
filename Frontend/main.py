from platform import system
from time import sleep
if system() == 'Windows':
    import sys
    sys.path.append('./')

from JunctionVisualiser import *
from JunctionDesigner import *


Visualiser = JunctionVisualiser()

def main():
    y = 0
    x = 100
    y_change = 1
    x_change = 1
    while(True):
        y = y + y_change
        x = x + x_change

        if y > 100:
            y_change = -5
            y = 100
        elif y < -100:
            y_change = 5
            y = -100

        if x > 100:
            x_change = -5
            x = 100
        elif x < -100:
            x_change = 5
            x = -100

        sleep(0.01)

        Visualiser.update_car_positions([[x, y]])


Visualiser.define_main(main)
Visualiser.load_junction("/Users/henrytriff/Documents/University/Work/Year 4/MECH5080 - Team Project/MECH5080M-TeamProject/Junction_Designs/Roundabout.junc")
Visualiser.set_scale(200)
Visualiser.open()
