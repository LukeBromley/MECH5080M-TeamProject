from platform import system

import tensorflow

if system() == 'Windows':
    import sys
    sys.path.append('./')

from simulation.simulation import Simulation
from gui.junction_visualiser import JunctionVisualiser
import os
from functools import partial

from tensorflow import keras, GradientTape, stop_gradient
from keras import layers, initializers
import numpy as np
from simulation.calculate_stats import Stats


# https://towardsdatascience.com/a-minimal-working-example-for-deep-q-learning-in-tensorflow-2-0-e0ca8a944d5e


class MachineLearning:
    def __init__(self, junction_file_path, config_file_path, visualiser_update_function=None):
        self.junction_file_path = junction_file_path
        self.config_file_path = config_file_path
        self.visualiser_update_function = visualiser_update_function

        # Simulation
        self.simulation = self.create_simulation()

        # Stats
        self.stats = Stats(self.simulation.model)

        # States
        self.max_number_of_vehicles = 10
        self.stats_per_vehicle = 4
        self.state_size = self.max_number_of_vehicles * self.stats_per_vehicle

        # Actions
        self.actions = self.calculate_all_actions()
        self.action_indexes = np.array([i for i in range(len(self.actions))])
        self.action_size = len(self.actions)

    def create_simulation(self):
        simulation = Simulation(self.junction_file_path, self.config_file_path, self.visualiser_update_function)
        simulation.model.setup_fixed_spawning(3)
        return simulation

    def calculate_all_actions(self):
        num_actions = 2**len(self.simulation.model.lights)
        actions = []
        for action in range(num_actions):
            binary = format(action, '0' + str(len(self.simulation.model.lights)) +'b')
            light_actions = []
            for char in binary:
                if char == '0':
                    light_actions.append('red')
                else:
                    light_actions.append('green')
            actions.append(light_actions)
        return actions

    def create_q_learning_model(self, state_size, action_size, hidden_layers):
        ml_layers = []
        ml_layers.append(layers.Input(shape=(state_size, )))  # input dimension
        for number_of_perceptrons in hidden_layers:
            ml_layers.append(layers.Dense(number_of_perceptrons, activation="relu", kernel_initializer=initializers.he_normal())(ml_layers[-1]))
        q_values = layers.Dense(action_size, kernel_initializer=initializers.Zeros(), activation="linear")(ml_layers[-1])
        q_network = keras.Model(inputs=ml_layers[0], outputs=[q_values])
        return q_network

    def save_model_weights(self, model, file_location, save_name):
        if os.path.isdir(file_location + "/" + save_name):
            os.mkdir(file_location + "/" + save_name)
        model.save_weights(file_location + "/" + save_name)

    def save_model(self, model, file_location, save_name):
        if os.path.isdir(file_location + "/" + save_name):
            os.mkdir(file_location + "/" + save_name)
        model.save(file_location + "/" + save_name)

    def load_weights(self, model, file_location, save_name):
        model.load_weights(file_location + "/" + save_name)
        return model

    def load_model(self, file_location, save_name):
        return keras.models.load_model(file_location + "/" + save_name)

    def train(self, number_of_episodes=10000, exploration_rate=0.01, learning_rate=0.01, file_location="trained_models", save_name="trained_model"):
        # Machine Learning Network
        q_learning_model = self.create_q_learning_model(self.state_size, self.action_size, hidden_layers=[25, 25, 25])

        # Machine Learning Optimiser
        opt = keras.optimizers.Adam(learning_rate=learning_rate)

        # Previous Actions
        prev_action = None

        # Loop Episodes
        for episode in range(number_of_episodes):
            with GradientTape() as tape:

                # Obtain Q-values from network
                # Essentially: Get the data from the simulation and give it to the neural netowrk
                state = self.get_state()
                q_values = q_learning_model(state)

                # Select action using epsilon-greedy policy
                # Essentially: Gets a random value. if the value is less than the exploration rate then explore
                #              else get the prediction from the network
                sample_epsilon = np.random.rand()
                if sample_epsilon <= exploration_rate:  # Select random action
                    action = np.random.choice(self.action_indexes)
                else:  # Select action with highest Q-value
                    action = np.argmax(q_values[0])

                if action != prev_action:
                    prev_action = action
                    self.do_action(action)

                self.simulation.run_single_iteration()

                reward = self.get_reward(episode)

                # Obtain Q-value
                q_value = q_values[0, action]

                # Compute loss value
                loss_value = self.get_loss(q_value, reward)

                "Compute gradients"
                grads = tape.gradient(loss_value, q_learning_model.trainable_variables)

                "Apply gradients to update network weights"
                opt.apply_gradients(zip(grads, q_learning_model.trainable_variables))

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

        self.save_model(q_learning_model, file_location, save_name)

    def run(self, number_of_episodes=10000, file_location="trained_models", save_name="trained_model"):
        self.stats.hide_graph()

        q_learning_model = self.load_model(file_location, save_name)

        prev_action = None
        for episode in range(number_of_episodes):
            state = self.get_state()

            q_values = q_learning_model(state)
            action = np.argmax(q_values[0])

            if action != prev_action:
                prev_action = action
                self.do_action(action)

            self.simulation.run_single_iteration()

            if episode % 10 == 0:
                print("Episode: " + str(episode))

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

    def do_action(self, action_index):
        action = self.actions[action_index]
        for index, light in enumerate(self.simulation.model.lights):
            self.simulation.model.set_state(light.uid, action[index])

    def get_reward(self, episode):
        return self.stats.get_reward(episode)

    def get_loss(self, q_value, reward):
        return 0.5 * (q_value - reward) ** 2


if __name__ == "__main__":
    # Reference Files
    junction_file_path = os.path.join(os.path.dirname(os.path.join(os.path.dirname(__file__))), "junctions", "cross_road.junc")
    configuration_file_path = os.path.join(os.path.dirname(os.path.join(os.path.dirname(__file__))), "configurations", "cross_road.config")

    # Settings
    scale = 100

    # Visualiser Init
    visualiser = JunctionVisualiser()

    # Simulation
    machine_learning = MachineLearning(junction_file_path, configuration_file_path, visualiser.update)

    # Visualiser Setup
    visualiser.define_main(machine_learning.train)
    visualiser.load_junction(junction_file_path)
    visualiser.set_scale(scale)

    # Run Simulation
    visualiser.open()

