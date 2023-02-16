from Library.vehicles import Vehicle
from Frontend.JunctionVisualiser import JunctionVisualiser
from Library.FileManagement import FileManagement

import time
from Constants import *

class Simulation:
    def __init__(self) -> None:
    
        self.vehicles = []
        self.car_uid = 0
        self.sim_time = 0.0
        self.log = []
        self.tick = 0.1

    def sim_begin(self):
        self.car_spawner()
        self.advance_tick()

    def advance_tick(self):
        self.update_cars()
        time.sleep(self.tick)
        self.sim_time = self.sim_time + self.tick
        if self.sim_time > 60:
            #self.log_writer()
            quit()
        else:
            self.advance_tick()

    def car_spawner(self):
        if len(self.cars) < 4:
            self.spawn_car()
        time.sleep(1)
        self.car_spawner()

    def spawn_car(self):
        uid = self.car_uid
        self.car_uid += 1
        random_start_lane = random.choice(LANES)
        goal_lane = random.choice(LANES)
        initial_velocity = random.uniform(
            MINIMUM_START_VELOCITY, MAXMUM_START_VELOCITY)
        initial_acceleration = random.uniform(
            MINIMUM_START_ACCELERATION, MAXIMUM_START_ACCELERATION)
        dimensions = [random.uniform(
            MIN_LENGTH, MAX_LENGTH), random.uniform(MIN_WIDTH, MAX_WIDTH)]
        car = Vehicle(uid, random_start_lane, goal_lane, initial_velocity,
                      initial_acceleration, dimensions)
        self.cars.append(car)

    # runs on tick
    def update_cars(self):
        for car in self.cars:
            car.update()
            self.log.append(car.log(self.sim_time))

    def log_writer(self):
        file = open('Backend/Approach/log.csv', 'w', newline='')
        writer = csv.writer(file)
        writer.writerows(self.log)
        file.close()


def main():
    sim = Simulation()
    sim.sim_begin()


main()
