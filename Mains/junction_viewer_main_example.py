from platform import system
import os
from time import sleep
if system() == 'Windows':
    import sys
    sys.path.append('./')

from Frontend.JunctionVisualiser import *
from Library.vehicles import Vehicle
from Library.environment import Time

Visualiser = JunctionVisualiser()


def main():
    y = 0
    x = 0
    a = 0
    y_change = 0.1
    x_change = 0.2
    a_change = 1

    vehicle = Vehicle(None)
    model = Model()
    model.load_config(os.path.join(os.path.dirname(__file__), "../Frontend/example_config.config"))
    model.add_light([1])

    for i in range(5000):
        y = y + y_change
        x = x + x_change
        a = a + a_change

        if i % 250 < 100:
            model.update_light(1, "red")
        else:
            model.update_light(1, "green")

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

        sleep(model.tick_time)
        model.tock()
        Visualiser.update_vehicle_positions([[x, y, a]])
        Visualiser.update_light_colours(model.lights)
        Visualiser.update_time(model.calculate_time_of_day())

        vehicle.position_data.append([x, y, a])
    model.vehicles.append(vehicle)
    model.save_results(os.path.join(os.path.dirname(__file__), "../Junction_Designs/test_results.res"))


Visualiser.define_main(main)
Visualiser.load_junction(os.path.join(os.path.dirname(__file__), "../Frontend/example_junction.junc"))
Visualiser.set_scale(200)
Visualiser.open()
