from time import sleep
from Frontend.JunctionVisualiser import JunctionVisualiser
from Library.infrastructure import Route
from Library.model import Model
from Library.vehicles import Car
from config import ROOT_DIR
import os
import random

class Simulation:
    def __init__(self, file_path: str):
        self.time = 0.0

        self.model = Model()
        self.model.load_junction(file_path)
        self._route_1 = Route([self.model.get_path(1), self.model.get_path(2), self.model.get_path(3)])
        self._route_2 = Route([self.model.get_path(4), self.model.get_path(5), self.model.get_path(6)])

        self.visualiser = JunctionVisualiser()
        self.visualiser.define_main(self.main)
        self.visualiser.load_junction(file_path)
        self.visualiser.set_scale(10)

    def main(self):
        dt = 0.01
        for x in range(10000):
            if random.random() > 0.99:
                self.add_vehicle(random.choice([self._route_1, self._route_2]))

            coordinates = []
            vehicles = [vehicle for vehicle in self.model.get_vehicles()]
            for index, vehicle in enumerate(vehicles):
                coordinates.append(vehicle.get_position())
                vehicle.update(dt, self.model.vehicles)
            self.visualiser.update_car_positions(coordinates)
            self.time += dt
            sleep(0.01)

    def run(self):
        self.visualiser.open()

    def add_vehicle(self, route: Route):
        self.model.add_vehicle(
            Car(
                uid=0,
                start_time=self.time,
                route=route,
                velocity=10.0,
                acceleration=0.0,
                maximum_acceleration=3.0,
                maximum_deceleration=6.0,
                preferred_time_gap=2.0,
                vehicle_length=4.0,
                maximum_velocity=30.0
            )
        )

if __name__ == "__main__":
    sim = Simulation(os.path.join(ROOT_DIR, "Junction_Designs", "cross_road.junc"))
    sim.run()

