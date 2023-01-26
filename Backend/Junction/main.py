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
                    uid="uid",
                    start_time=0,
                    position_data=None,
                    path=path,
                    velocity=0.0,
                    acceleration=0.0,
                    maximum_acceleration=5.0,
                    maximum_deceleration=4.0,
                    distance_traveled=0,
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
            self.vehicles = [vehicle for vehicle in self.vehicles if vehicle.get_cartesian_position() is not None]
            for index, vehicle in enumerate(self.vehicles):
                vehicle.update(dt)
                coordinates.append(vehicle.get_cartesian_position())
            self.visualiser.update_car_positions(coordinates)
            time.sleep(0.01)

    def run(self):
        self.visualiser.open()


if __name__ == "__main__":
    sim = Simulation(os.path.join(ROOT_DIR, "Junction_Designs", "test.junc"))
    sim.run()

