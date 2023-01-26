import time

from Frontend.JunctionVisualiser import JunctionVisualiser
from Library.FileManagement import FileManagement
from Library.vehicles import Car
from config import ROOT_DIR
import os


class Simulation:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.nodes, self.paths, self.lights = FileManagement().load_from_junction_file(file_path)
        self.vehicles = []

        for path in self.paths:
            self.vehicles.append(
                Car(
                    uid=0,
                    start_time=0,
                    path=path,
                    velocity=0.0,
                    acceleration=0.0,
                    maximum_acceleration=3.0,
                    maximum_deceleration=6.0,
                    preferred_time_gap=2.0,
                    vehicle_length=4.0,
                    maximum_velocity=30.0
                )
            )
            break

        self.visualiser = JunctionVisualiser()
        self.visualiser.define_main(self.main)
        self.visualiser.load_junction(file_path)
        self.visualiser.set_scale(50)

    def main(self):
        dt = 0.01
        for x in range(1000):
            coordinates = []
            self.vehicles = [vehicle for vehicle in self.vehicles if vehicle.get_position() is not None]
            for index, vehicle in enumerate(self.vehicles):
                coordinates.append(vehicle.get_position())
                vehicle.update(dt, self.vehicles)
            self.visualiser.update_car_positions(coordinates)
            time.sleep(0.01)

    def run(self):
        self.visualiser.open()


if __name__ == "__main__":
    sim = Simulation(os.path.join(ROOT_DIR, "Junction_Designs", "test.junc"))
    sim.run()

