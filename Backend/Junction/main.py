from platform import system
if system() == 'Windows':
    import sys
    sys.path.append('./')

import time

from Frontend.JunctionVisualiser import JunctionVisualiser
from Library.FileManagement import FileManagement
from Library.infrastructure import Route
from Library.model import Model
from Library.vehicles import Car
from config import ROOT_DIR
import os


class Simulation:
    def __init__(self, file_path: str):
        self.model = Model()
        self.model.load_junction(file_path)
        self.model.generate_routes()
        self.model.add_vehicle(
            
            Car(
                uid=0,
                start_time=0,
                route=self.model.get_route(),
                velocity=0.0,
                acceleration=0.0,
                maximum_acceleration=3.0,
                maximum_deceleration=6.0,
                preferred_time_gap=2.0,
                vehicle_length=4.0,
                maximum_velocity=30.0
            )
        )

        self.visualiser = JunctionVisualiser()
        self.visualiser.define_main(self.main)
        self.visualiser.load_junction(file_path)
        self.visualiser.set_scale(50)

    def main(self):
        dt = 0.01
        for x in range(1000):
            coordinates = []
            vehicles = [vehicle for vehicle in self.model.vehicles if vehicle.get_position() is not None]
            for index, vehicle in enumerate(vehicles):
                coordinates.append(vehicle.get_position())
                vehicle.update(dt, self.model.vehicles)
            self.visualiser.update_car_positions(coordinates)
            time.sleep(0.01)

    def run(self):
        self.visualiser.open()


if __name__ == "__main__":
    sim = Simulation(os.path.join(ROOT_DIR,"Junction_Designs", "Roundabout2.junc"))
    sim.run()
