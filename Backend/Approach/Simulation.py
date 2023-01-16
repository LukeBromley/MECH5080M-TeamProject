from Constants import *
import random
import time


class Car:
    def __init__(self, random_start_lane, goal_lane, initial_velocity, initial_acceleration, dimensions) -> None:
        self.current_lane = random_start_lane
        self.goal_lane = goal_lane
        self.velocity = initial_velocity
        self.acceleration = initial_acceleration
        self.dimensions = dimensions

    def display_car(self):
        print("Current Lane = ", self.current_lane)
        print("Goal Lane = ", self.goal_lane)
        print("Velocity = ", self.velocity)
        print("Acceleration = ", self.acceleration)
        print("Dimensions = Length: ",
              self.dimensions[0], ", Width: ", self.dimensions[1])


class Simulation:

    def __init__(self) -> None:
        self.cars = []
        self.sim_tick()

    def sim_tick(self):
        print("Tick")
        self.car_spawner()
        self.run_cars()
        time.sleep(1)
        self.sim_tick()

    def car_spawner(self):
        if len(self.cars) < MAX_CARS:
            self.spawn_car()

    def spawn_car(self):
        random_start_lane = random.choice(LANES)
        goal_lane = random.choice(LANES)
        initial_velocity = random.uniform(
            MINIMUM_START_VELOCITY, MAXMUM_START_VELOCITY)
        initial_acceleration = random.uniform(
            MINIMUM_START_ACCELERATION, MAXIMUM_START_ACCELERATION)
        dimensions = [random.uniform(
            MIN_LENGTH, MAX_LENGTH), random.uniform(MIN_WIDTH, MAX_WIDTH)]
        car = Car(random_start_lane, goal_lane, initial_velocity,
                  initial_acceleration, dimensions)
        self.cars.append(car)

    # runs on tick
    def run_cars(self):
        for car in self.cars:
            car.display_car()


def main():
    sim = Simulation()


main()
