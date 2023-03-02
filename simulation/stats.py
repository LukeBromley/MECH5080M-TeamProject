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
