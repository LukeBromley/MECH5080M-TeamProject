from platform import system
import os
if system() == 'Windows':
    import sys
    sys.path.append('./')

from Frontend.JunctionVisualiser import *

Visualiser = JunctionVisualiser()

def main():
    # Run simulation here
    Visualiser.update_vehicle_positions([[0, 0]])


Visualiser.define_main(main)
Visualiser.load_junction(os.path.join(os.path.dirname(__file__), "../Frontend/example_junction.junc"))
Visualiser.set_scale(50)
Visualiser.open()
