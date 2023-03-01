import matplotlib.pyplot as plt
import numpy as np
from numpy import mean

class Stats:
    def __init__(self, model):
        self.model = model

        self.default_reward = 1
        self.reward_last_100_episodes = []

        # CRASH
        # Reward
        self.crash_reward = -100

        # WAITING
        # Parameters
        self.waiting_speed = 0.2

        # Reward
        self.num_waiting_reward = -5
        self.waiting_reward = -1

        self.all_wait_times = []
        self.avg_waiting_reward = 0

        # SPEED
        # Reward
        self.speed_reward = 1

        # COMPLETE
        # Reward
        self.complete_reward = 10

        # GRAPHING
        # to run GUI event loop
        plt.ion()

        # here we are creating sub plots
        self.figure, self.graph = plt.subplots(figsize=(10, 8))

        # setting title
        plt.title("Reward", fontsize=20)

        # setting x-axis label and y-axis label
        plt.xlabel("X-axis")
        plt.ylabel("Y-axis")
        plt.ylim([-1000, 100])

        self.x = [i for i in range(100)]
        self.y = [0 for i in range(100)]

        self.line1, = self.graph.plot(self.x, self.y)

    def get_reward(self, episode):
        self.reward = self.default_reward
        self.reward += self.crash_reward * self.get_crash()
        # self.reward += self.num_waiting_reward * self.get_number_of_cars_waiting()
        # self.reward += self.waiting_reward * self.get_car_wait_time()
        self.reward += self.waiting_reward * self.get_car_wait_time_powered(1.3)
        self.reward += self.speed_reward * self.get_speed_of_all_cars()
        self.reward += self.complete_reward * self.get_cars_finished()

        if episode % 10 == 0:
            avg_reward = sum(self.reward_last_100_episodes) / 10
            self.update_graph(episode, avg_reward)
            self.reward_last_100_episodes.clear()
        self.reward_last_100_episodes.append(self.reward)

        return self.reward

    def get_crash(self):
        return 1 if len(self.model.detect_collisions()) > 0 else 0

    def get_number_of_cars_waiting(self):
        number_of_cars_waiting = 0
        for vehicle in self.model.vehicles:
            if vehicle.get_speed() < self.waiting_speed:
                number_of_cars_waiting += 1
        return number_of_cars_waiting

    def update_waiting_vehicles(self):
        for vehicle in self.model.vehicles:
            if vehicle.get_speed() < self.waiting_speed:
                vehicle.waiting_time += self.model.tick_time

    def get_car_wait_time(self):
        self.update_waiting_vehicles()
        total_wait_time = 0
        for vehicle in self.model.vehicles:
            total_wait_time += vehicle.waiting_time
        return total_wait_time

    def get_car_wait_time_powered(self, power):
        self.update_waiting_vehicles()
        total_wait_time = 0
        for vehicle in self.model.vehicles:
            total_wait_time += vehicle.waiting_time**power
        return total_wait_time

    def get_speed_of_all_cars(self):
        sum_car_speed = 0
        for vehicle in self.model.vehicles:
            sum_car_speed += vehicle.get_speed()
        return sum_car_speed

    def get_cars_finished(self):
        # THIS HAS BEEN COMPLETED IN A JUNCTION SPECIFIC WAY..... NEEDS TO BE IMPLEMENTED PROPERLY
        number_of_cars_finished = 0
        for vehicle in self.model.vehicles:
            if vehicle.get_path_index() > 1:
                number_of_cars_finished += 1
                self.all_wait_times.append(vehicle.waiting_time)
        return number_of_cars_finished

    # This function is called periodically from FuncAnimation
    def update_graph(self, episode, reward):
        # self.x.append(episode)
        # self.x = self.x[-1000:]
        self.y.append(reward)
        self.y = self.y[-100:]

        self.line1.set_xdata(self.x)
        self.line1.set_ydata(self.y)

        # drawing updated values
        self.figure.canvas.draw()

        # This will run the GUI event
        # loop until all UI events
        # currently waiting have been processed
        self.figure.canvas.flush_events()

    def hide_graph(self):
        plt.close()


class Controller:
    def __init__(self, model):
        self.model = model

        # State
        self.wait_time = None
        self.wait_time_vehicle_limit = None
        self.collision = None

        # Action

        # Reward
        self.reward = 0
        self.total_reward = 0

    def reset(self):
        # State
        self.wait_time = [0]
        self.wait_time_vehicle_limit = 50
        self.collision = None

        # Action

        # Reward
        self.reward = 0
        self.total_reward = 0

    def get_reward(self):
        self.reward = 30 - self.get_mean_wait_time() ** 2 + penalty + (i / 1000)
        if self.collision is not None:
            self.reward -= 5000

        self.total_reward += self.reward

    def take_action(self, action_index):
        penalty = 0
        if action_index == 0:
            pass
        elif action_index == 1:
            if self.model.get_lights()[0] == "green":
                self.set_red(0)
            else:
                penalty = -10000
        elif action_index == 2:
            if self.model.get_lights()[1] == "green":
                self.set_red(1)
            else:
                penalty = -10000
        return penalty

    def set_red(self, index):
        self.model.get_lights()[index].set_red()

    def get_state(self):
        return np.array(
            [
                self.get_path_occupancy(1),
                self.get_path_wait_time(1),
                self.get_mean_speed(1),
                self.get_path_occupancy(4),
                self.get_path_wait_time(4),
                self.get_mean_speed(4),
                self.model.get_lights()[0].get_state(),
                self.model.get_lights()[0].get_time_remaining(),
                self.model.get_lights()[1].get_state(),
                self.model.get_lights()[1].get_time_remaining(),
            ]
        )

    def get_path_occupancy(self, path_uid):
        state = 0
        for vehicle in self.model.vehicles:
            route = self.model.get_route(vehicle.get_route_uid())
            if path_uid == route.get_path_uid(vehicle.get_path_index()):
                state += 1
        return state

    def get_path_wait_time(self, path_uid):
        wait_time = 0
        for vehicle in self.model.vehicles:
            route = self.model.get_route(vehicle.get_route_uid())
            if path_uid == route.get_path_uid(vehicle.get_path_index()):
                wait_time += vehicle.get_wait_time()
        return wait_time

    def get_mean_speed(self, path_uid):
        speed = []
        for vehicle in self.model.vehicles:
            route = self.model.get_route(vehicle.get_route_uid())
            if path_uid == route.get_path_uid(vehicle.get_path_index()):
                speed.append(vehicle.get_speed())
        return mean(speed)

    def get_mean_wait_time(self):
        return mean(self.wait_time)

    def get_lights(self):
        return self.model.get_lights()