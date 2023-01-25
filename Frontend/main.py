from platform import system
if system() == 'Windows':
    import sys
    sys.path.append('./')

from JunctionVisualiser import *
from JunctionDesigner import *

Visualiser = JunctionVisualiser()


def main():
    i=0
    for i in range(100000):
        print(i)
        i+=1


Visualiser.define_main(main)
Visualiser.load_junction("/Users/henrytriff/Documents/University/Work/Year 4/MECH5080 - Team Project/MECH5080M-TeamProject/Junction_Designs/Roundabout.junc")
Visualiser.open()
