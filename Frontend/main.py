import sys
sys.path.append("..")
from JunctionVisualiser import *
from Backend.Library.Infrastructure import Lane


lanes = [
    Lane(100, 100, 0),
    Lane(200, 200, 0)
]


def main():
    Visualiser = JunctionVisualiser()
    while True:
        Visualiser.run()
        Visualiser.draw_lanes(lanes)
        Visualiser.update()


if __name__ == "__main__":
    main()