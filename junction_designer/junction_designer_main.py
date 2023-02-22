from platform import system
if system() == 'Windows':
    import sys
    sys.path.append('../Mains/')

from gui.junction_designer import *

Visualiser = JunctionDesigner()
