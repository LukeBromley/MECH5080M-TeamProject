from platform import system
if system() == 'Windows':
    import sys
    sys.path.append('./')

from JunctionVisualiser import *


# Main function
def main() -> None:
    """

    Main function to test and run the junction visualiser
    :return: None
    """
    Visualiser = JunctionVisualiser()


if __name__ == "__main__":
    main()
