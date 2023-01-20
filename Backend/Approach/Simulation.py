from Constants import *
import random
import time
import csv


class Car:
    def __init__(self, uid, random_start_lane, goal_lane, initial_velocity, initial_acceleration, dimensions) -> None:
        self.uid = uid
        self.current_lane = random_start_lane
        self.position = [0, 0]  # Change to psoition of lane.
        self.goal_lane = goal_lane
        self.velocity = initial_velocity
        self.acceleration = initial_acceleration
        self.dimensions = dimensions

    def print_car(self):
        print("Current Lane = ", self.current_lane)
        print("Goal Lane = ", self.goal_lane)
        print("Velocity = ", self.velocity)
        print("Acceleration = ", self.acceleration)
        print("Dimensions = Length: ",
              self.dimensions[0], ", Width: ", self.dimensions[1])

    def update(self):
        self.position[0] += self.velocity
        self.position[1] += self.velocity
        self.velocity += self.acceleration

    def log(self, sim_time):
        log_format = [sim_time, self.uid, self.position[0], self.position[1]]
        return log_format


class Simulation:

    def __init__(self) -> None:
        self.cars = []
        self.car_uid = 0
        self.sim_time = 0.0
        self.log = []

    def sim_begin(self):
        self.advance_tick()

    def advance_tick(self):
        self.car_spawner()
        self.update_cars()
        time.sleep(TICK)
        self.sim_time = round(self.sim_time + TICK, 1)
        if self.sim_time > 3:
            self.log_writer()
            quit()
        else:
            self.advance_tick()

    def car_spawner(self):
        if len(self.cars) < MAX_CARS:
            self.spawn_car()

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
        car = Car(uid, random_start_lane, goal_lane, initial_velocity,
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
