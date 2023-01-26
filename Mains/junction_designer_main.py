from platform import system
if system() == 'Windows':
    import sys
    sys.path.append('./')

from Frontend.JunctionDesigner import *

Visualiser = JunctionDesigner()
