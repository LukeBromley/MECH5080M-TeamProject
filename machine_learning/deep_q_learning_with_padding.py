from platform import system

import tensorflow

if system() == 'Windows':
    import sys
    sys.path.append('./')

from simulation.simulation import Simulation
from gui.junction_visualiser import JunctionVisualiser
import os

from tensorflow import keras, GradientTape, stop_gradient
from keras import layers, initializers
import numpy as np
from simulation.calculate_stats import Stats


# https://towardsdatascience.com/a-minimal-working-example-for-deep-q-learning-in-tensorflow-2-0-e0ca8a944d5e


class MachineLearning:
    def __init__(self, junction_file_path, config_file_path, visualiser_update_function = None):
        self.junction_file_path = junction_file_path
        self.config_file_path = config_file_path
        self.visualiser_update_function = visualiser_update_function

        # Simulation
        self.simulation = None
        self.reset_sumulation()

        # Stats
        self.stats = Stats(self.simulation.model)

        # Input
        self.max_number_of_vehicles = 20
        self.stats_per_vehicle = 4
        self.state_size = self.max_number_of_vehicles * self.stats_per_vehicle

        # Outputs
        self.traffic_light_actions = np.array([0, 1, 2, 3])
        self.action_size = len(self.traffic_light_actions)

        # Training
        self.number_of_episodes = 10000
        self.exploration_rate = 0.01
        self.learning_rate = 0.05

        # Machine Learning Network
        self.network = self.create_q_learning_network(self.state_size, self.action_size)

    def reset_sumulation(self):
        self.simulation = Simulation(self.junction_file_path, self.config_file_path, self.visualiser_update_function)
        self.simulation.model.setup_fixed_spawning(3)

    def create_q_learning_network(self, state_size, action_size):
        inputs = layers.Input(shape=(state_size, ))  # input dimension
        hidden1 = layers.Dense(25, activation="relu", kernel_initializer=initializers.he_normal())(inputs)
        hidden2 = layers.Dense(25, activation="relu", kernel_initializer=initializers.he_normal())(hidden1)
        hidden3 = layers.Dense(25, activation="relu", kernel_initializer=initializers.he_normal())(hidden2)
        q_values = layers.Dense(action_size, kernel_initializer=initializers.Zeros(), activation="linear")(hidden3)

        q_network = keras.Model(inputs=inputs, outputs=[q_values])
        return q_network

    def run(self):
        opt = keras.optimizers.Adam(learning_rate=self.learning_rate)
        prev_action = None

        for episode in range(self.number_of_episodes):
            with GradientTape() as tape:

                # Obtain Q-values from network
                # Essentially: Get the data from the simulation and give it to the neural netowrk
                state = self.get_state()
                q_values = self.network(state)

                # Select action using epsilon-greedy policy
                # Essentially: Gets a random value. if the value is less than the exploration rate then explore
                #              else get the prediction from the network
                sample_epsilon = np.random.rand()
                if sample_epsilon <= self.exploration_rate:  # Select random action
                    action = np.random.choice(self.traffic_light_actions)
                else:  # Select action with highest Q-value
                    action = np.argmax(q_values[0])

                if action != prev_action:
                    prev_action = action
                    if action == 0:
                        self.simulation.model.set_state(1, 'red')
                        self.simulation.model.set_state(2, 'red')
                    elif action == 1:
                        self.simulation.model.set_state(1, 'green')
                        self.simulation.model.set_state(2, 'green')
                    elif action == 2:
                        self.simulation.model.set_state(1, 'red')
                        self.simulation.model.set_state(2, 'green')
                    elif action == 3:
                        self.simulation.model.set_state(1, 'green')
                        self.simulation.model.set_state(2, 'red')

                self.simulation.run_single_iteration()

                reward = self.get_reward(episode)

                # Obtain Q-value
                q_value = q_values[0, action]

                # Compute loss value
                loss_value = self.get_loss(q_value, reward)

                "Compute gradients"
                grads = tape.gradient(loss_value, self.network.trainable_variables)

                "Apply gradients to update network weights"
                opt.apply_gradients(zip(grads, self.network.trainable_variables))

                if episode % 10 == 0:
                    print("Episode: " + str(episode) + ", Reward: " + str(reward))

                # "Obtain Q-value for selected action"
                # q_value = q_values[0, action]
                #
                # "Determine next state"
                # next_state = get_state(state, action)
                #
                # "Select next action with highest Q-value"
                # if next_state == terminal_state:
                #     next_q_value = 0  # No Q-value for terminal
                # else:
                #     next_q_values = stop_gradient(self.network(next_state))  # No gradient computation
                #     next_action = np.argmax(next_q_values[0])
                #     next_q_value = next_q_values[0, next_action]
                #
                # "Compute observed Q-value"
                # observed_q_value = reward + (self.learning_rate * next_q_value)
                #
                # "Compute loss value"
                # loss_value = (observed_q_value - current_q_value) ** 2
                #
                # "Compute gradients"
                # grads = tape.gradient(loss_value, self.network.trainable_variables)
                #
                # "Apply gradients to update network weights"
                # opt.apply_gradients(zip(grads, self.network.trainable_variables))
                #
                # "Update state"
                # state = next_state

    def get_state(self):
        data = []

        for vehicle in self.simulation.model.vehicles[:self.max_number_of_vehicles]:
            speed = vehicle.get_speed()
            coordinates = self.simulation.model.get_vehicle_coordinates(vehicle.uid)
            data += [speed, coordinates[0], coordinates[1], 1]

        while len(data) < self.state_size:
            data += [0, 0, 0, 0]

        data = tensorflow.constant([data])

        return data

    def get_reward(self, episode):
        total_reward = self.stats.get_reward(episode)

        return total_reward

    def get_loss(self, q_value, reward):
        """Compute mean squared error loss"""
        loss = 0.5 * (q_value - reward) ** 2

        return loss


if __name__ == "__main__":
    # Reference Files
    junction_file_path = os.path.join(os.path.dirname(os.path.join(os.path.dirname(__file__))), "junctions", "cross_road.junc")
    configuration_file_path = os.path.join(os.path.dirname(os.path.join(os.path.dirname(__file__))), "configurations", "cross_road.config")

    # Settings
    scale = 100
    speed_multiplier = 5

    # Visualiser Init
    visualiser = JunctionVisualiser()

    # Simulation
    machine_learning = MachineLearning(junction_file_path, configuration_file_path, visualiser.update)

    # Visualiser Setup
    visualiser.define_main(machine_learning.run)
    visualiser.load_junction(junction_file_path)
    visualiser.set_scale(scale)

    # Run Simulation
    visualiser.open()

