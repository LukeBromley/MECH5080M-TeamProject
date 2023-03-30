import copy
import math
import random
from math import sqrt
from platform import system
import sys

from matplotlib import pyplot as plt
from pynput import keyboard

if system() == 'Windows':
    sys.path.append('./')

import os
import sys
from simulation.junction.simulation_manager import SimulationManager
from analysis_tools.graph_ml_progress import Graph
from gui.junction_visualiser import JunctionVisualiser
from time import sleep
import time as tm

import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

# https://towardsdatascience.com/a-minimal-working-example-for-deep-q-learning-in-tensorflow-2-0-e0ca8a944d5e


class MachineLearning:
    def __init__(self, simulation_manager: SimulationManager, machine_learning_config=None, graph_num_episodes=20, graph_max_step=30000):
        # SIMULATION MANAGER
        self.future_wait_time = None
        self.simulation_manager = simulation_manager

        # TODO: Profile code
        # GRAPH
        # self.graph = Graph(graph_num_episodes, graph_max_step)
        self.data = []

        # COUNTERS
        self.episode_count = 0  # Number of episodes trained
        self.number_of_steps_taken = 0  # Total number of steps taken over all episodes
        self.all_time_reward = 0  # Total reward over all episodes

        # TRAINING LIMITS
        self.max_episode_length_in_seconds = 60
        self.max_steps_per_episode = self.max_episode_length_in_seconds * self.simulation_manager.simulation.model.tick_rate  # Maximum number of steps allowed per episode
        self.episode_end_reward = -100000  # Single episode total reward minimum threshold to end episode. Should be low to allow exploration
        self.solved_mean_reward = float("inf")  # Single episode total reward minimum threshold to consider ML trained
        self.reward_history_limit = 20
        self.max_mean_reward_solved = self.episode_end_reward

        # TAKING AN ACTION
        # Probability of selecting a random action
        self.epsilon_greedy_min = 0.1  # Minimum probability of selecting a random action - zero to avoid future collision penalties
        self.epsilon_greedy_max = 1.0  # Maximum probability of selecting a random action
        self.epsilon_greedy = self.epsilon_greedy_max  # Current probability of selecting a random action

        # Exploration
        # Number of steps of just random actions before the network can make some decisions
        self.number_of_steps_of_required_exploration = 1000
        # Number of steps over which epsilon greedy decays
        self.number_of_steps_of_exploration_reduction = 20000
        # Train the model after 4 actions
        self.update_after_actions = 7
        # How often to update the target network
        self.update_target_network = 500
        # Penalty for collision
        self.collision_penalty = 1000

        # REPLAY
        # Buffers
        self.action_history = []
        self.state_history = []
        self.rewards_history = []
        self.done_history = []
        self.episode_reward_history = []

        # Steps to look into the future to determine the mean reward. Should match T = 1/(1-gamma)
        self.number_of_temporal_difference_steps = 5 * self.simulation_manager.simulation.model.tick_rate

        # Sample Size
        self.sample_size = 32  # Size of batch taken from replay buffer

        # Discount factor
        self.gamma = 0.99  # Discount factor for past rewards

        # Maximum replay buffer length
        # Note: The Deepmind paper suggests 1000000 however this causes memory issues
        self.max_replay_buffer_length = 500000

        # OPTIMISING
        # Note: In the Deepmind paper they use RMSProp however then Adam optimizer
        self.learning_rate = 0.0001  # 0.00025
        self.optimizer = keras.optimizers.legacy.Adam(learning_rate=self.learning_rate, clipnorm=1.0)

        # OTHER
        # Using huber loss for stability
        self.loss_function = keras.losses.Huber()

        # MACHINE LEARNING MODELS
        n = self.simulation_manager.observation_space_size
        self.ml_model_hidden_layers = [n, n, n, n]

        # Change configurations to ones supplied in machine_learning_config
        if machine_learning_config is not None:
            self.apply_ML_configurations(machine_learning_config)

        # Makes the predictions for Q-values which are used to make a action.
        self.ml_model = self.create_q_learning_model(self.simulation_manager.observation_space_size, self.simulation_manager.number_of_possible_actions, self.ml_model_hidden_layers)
        # For the prediction of future rewards. The weights of a target model get updated every 10000 steps thus when the loss between the Q-values is calculated the target Q-value is stable.
        self.ml_model_target = self.create_q_learning_model(self.simulation_manager.observation_space_size, self.simulation_manager.number_of_possible_actions, self.ml_model_hidden_layers)

    def apply_ML_configurations(self, config):
        self.max_steps_per_episode = config.max_steps_per_episode
        self.episode_end_reward = config.episode_end_reward
        self.solved_mean_reward = config.solved_mean_reward
        self.reward_history_limit = config.reward_history_limit
        self.random_action_selection_probabilities = config.random_action_selection_probabilities
        self.epsilon_greedy_min = config.epsilon_greedy_min
        self.epsilon_greedy_max = config.epsilon_greedy_max
        self.number_of_steps_of_required_exploration = config.number_of_steps_of_required_exploration
        self.number_of_steps_of_exploration_reduction = config.number_of_steps_of_exploration_reduction
        self.update_after_actions = config.update_after_actions
        self.update_target_network = config.update_target_network
        self.seconds_to_look_into_the_future = config.seconds_to_look_into_the_future
        self.sample_size = config.sample_size
        self.gamma = config.gamma
        self.max_replay_buffer_length = config.max_replay_buffer_length
        self.learning_rate = config.learning_rate
        self.ml_model_hidden_layers = config.ml_model_hidden_layers

    def create_q_learning_model(self, state_size, action_size, hidden_layers):
        ml_layers = [layers.Input(shape=(state_size, ))]  # input dimension
        for number_of_perceptrons in hidden_layers:
            ml_layers.append(layers.Dense(number_of_perceptrons, activation="relu")(ml_layers[-1]))
        q_values = layers.Dense(action_size, activation="linear")(ml_layers[-1])
        q_network = tf.keras.models.Model(inputs=ml_layers[0], outputs=[q_values])
        return q_network

    def train(self):
        mean_reward = 0
        while True:  # Run until solved
            state = self.simulation_manager.reset()
            episode_reward = 0
            episode_step = 0

            # Run steps in episode
            while True:

                # Increment the episode step
                episode_step += 1

                # Determine legal actions
                legal_actions = self.simulation_manager.get_legal_actions()

                if len(legal_actions) == 1:
                    # TODO: instead of skipping sum the rewards and assign to the previous action
                    self.step(legal_actions[0], td=False)
                    self.end_episode(episode_reward, episode_step)
                    continue

                state = self.simulation_manager.get_state()


                # Select an action
                action_index = self.select_action(state)

                # Step the simulation
                reward = self.step(action_index, td=True)

                # Record next state
                next_state = self.simulation_manager.get_state()

                # Update episode reward
                episode_reward += reward

                # Determine if episode is over
                done = self.end_episode(episode_reward, episode_step)

                # Save actions and states in replay buffer
                self.save_to_replay_buffers(action_index, state, next_state, done, reward)

                # Increment the total number of steps taken by the AI in total.
                self.number_of_steps_taken += 1

                # Update
                if self.number_of_steps_taken % self.update_after_actions == 0 and len(self.done_history) > self.sample_size:

                    state_sample, state_next_sample, rewards_sample, action_sample, done_sample = self.sample_replay_buffers()
                    updated_q_values = self.calculate_updated_q_values(state_next_sample, rewards_sample, done_sample)

                    # Create a mask so we only calculate loss on the updated Q-values
                    masks = tf.one_hot(action_sample, self.simulation_manager.number_of_possible_actions)

                    with tf.GradientTape() as tape:
                        # Train the model on the states and updated Q-values
                        q_values = self.ml_model(state_sample)

                        # Apply the masks to the Q-values to get the Q-value for action taken
                        q_action = tf.reduce_sum(tf.multiply(q_values, masks), axis=1)

                        # Calculate loss between new Q-value and old Q-value
                        loss = self.loss_function(updated_q_values, q_action)

                    # Backpropagation
                    grads = tape.gradient(loss, self.ml_model.trainable_variables)
                    self.optimizer.apply_gradients(zip(grads, self.ml_model.trainable_variables))

                if self.number_of_steps_taken % self.update_target_network == 0:
                    # update the target network with new weights
                    self.ml_model_target.set_weights(self.ml_model.get_weights())
                    # Log details
                    print(f'{tm.strftime("%H:%M:%S", tm.localtime())}  -  {self.get_mean_reward():.2f} / {self.solved_mean_reward:.2f} at episode {self.episode_count}; frame count: {self.number_of_steps_taken}.')
                    if self.get_mean_reward() > self.max_mean_reward_solved:
                        self.max_mean_reward_solved = self.get_mean_reward()
                        self.ml_model_target.save("saved_model" + str(round(self.get_mean_reward())))
                        print(f'{tm.strftime("%H:%M:%S", tm.localtime())}  -  SavedModel recorded.')
                # Delete old buffer values
                self.delete_old_replay_buffer_values()

                if done:
                    break

            # print(action_log)
            self.episode_reward_history.append(episode_reward)
            self.episode_count += 1

            if self.solved(self.get_mean_reward()):
                self.ml_model_target.save("saved_model")
                break
        return self.get_mean_reward()

    def step(self, action_index: int, td: bool = True):
        # More than two actions available guaranteed
        reward = 0
        state_value = self.simulation_manager.get_sum_wait_time()
        self.take_action(action_index)
        self.simulation_manager.simulation.compute_single_iteration()
        # if self.simulation_manager.simulation.model.detect_collisions():
        #     reward += self.collision_penalty

        reward += (state_value - self.simulation_manager.get_sum_wait_time())

        if td:
            reward += self.calculate_temporal_difference_reward(copy.deepcopy(self.simulation_manager))
        # TODO: Reward Shaping

        # TODO: Temporal Credit Assignment

        # TODO: Prioritised sweeping

        # TODO: implement light timings and set red after the light turns green and simulate for infinite amount of time to look for a cloosion

        # TODO: mean_wait_time is the same if one or two lanes are held red
        return reward

    def calculate_temporal_difference_reward(self, simulation_manager: SimulationManager):
        reward = 0
        # state_value = simulation_manager.get_sum_wait_time()
        rewards = []
        # TODO: Try reset after every action
        for index in range(1, self.number_of_temporal_difference_steps):
            state_value = simulation_manager.get_sum_wait_time()
            temporal_difference_reward = 0
            simulation_manager.take_action(self.select_action(simulation_manager.get_state(), target=True))
            simulation_manager.simulation.compute_single_iteration()

            if simulation_manager.simulation.model.detect_collisions():
                temporal_difference_reward -= self.collision_penalty

            temporal_difference_reward += (state_value - simulation_manager.get_sum_wait_time())
            reward += math.pow(self.gamma, index) * temporal_difference_reward
            rewards.append(math.pow(self.gamma, index) * temporal_difference_reward)
        # print(rewards)
        return reward

    def detect_collision(self, simulation_manager: SimulationManager):
        # TODO: Temporal credit assignment
        for light in simulation_manager.simulation.model.lights:
            light.colour = "red"

        min_vehicle_speed = 100
        while min_vehicle_speed > 1:
            simulation_manager.simulation.compute_single_iteration()
            if self.simulation_manager.simulation.model.detect_collisions():
                return True
            min_vehicle_speed = min([vehicle.get_speed() for vehicle in simulation_manager.simulation.model.vehicles])
        return False

    def select_action(self, state, target: bool = False):
        if target:
            action = self.select_best_action(state, target)
        else:
            # Exploration vs Exploitation
            if self.number_of_steps_taken < self.number_of_steps_of_required_exploration or self.epsilon_greedy > np.random.rand(1)[0]:
                # Take random action
                action = self.select_random_action()
            else:
                # Take best action
                action = self.select_best_action(state)

            self.update_epsilon_greedy()
        return action

    def select_random_action(self):
        legal_actions = self.simulation_manager.get_legal_actions()
        if legal_actions:
            if len(legal_actions) == 1:
                return legal_actions[0]

            p = []
            for action_index in legal_actions:
                do_nothing_probability = 0.95
                if action_index != self.simulation_manager.do_nothing_action_index:
                    p.append((1 - do_nothing_probability) / (len(legal_actions) - 1))
                else:
                    p.append(do_nothing_probability)
            return np.random.choice(legal_actions, p=p)

    def select_best_action(self, state, target: bool = False):
        # Predict action Q-values
        # From simulation_manager state
        legal_actions = self.simulation_manager.get_legal_actions()
        if len(legal_actions) == 1:
            return legal_actions[0]

        state_tensor = tf.expand_dims(tf.convert_to_tensor(state), 0)
        illegal_actions = self.simulation_manager.get_illegal_actions()
        if target:
            action_probs = self.ml_model_target(state_tensor, training=False)[0].numpy()
        else:
            action_probs = self.ml_model(state_tensor, training=False)[0].numpy()
        action_probs[illegal_actions] = np.NAN
        return np.nanargmax(action_probs)

    def update_epsilon_greedy(self):
        if self.epsilon_greedy >= self.epsilon_greedy_min:
            self.epsilon_greedy -= (self.epsilon_greedy_max - self.epsilon_greedy_min) / self.number_of_steps_of_exploration_reduction

    def take_action(self, action_index):
        self.simulation_manager.take_action(action_index)

    def end_episode(self, episode_reward, step):
        if episode_reward < self.episode_end_reward or step > self.max_steps_per_episode:
            # print(f"   - Score: {episode_reward:.2f} / Steps: {step}")
            # print("Score at episode end:", episode_reward, "/ Steps:", step)
            # sys.stdout.write("\rEpisode: {0} / Mean Reward: {1}".format(str(episode_reward), str(step)))
            # sys.stdout.flush()
            return True
        else:
            return False

    def save_to_replay_buffers(self, action, state, next_state, done, reward):
        self.action_history.append(action)
        self.state_history.append(state)
        # self.state_next_history.append(next_state)
        self.done_history.append(done)
        self.rewards_history.append(reward)

    def sample_replay_buffers(self):
        # TODO: Implement prioritised sweeping

        # Get indices of samples for replay buffers
        indices = self.get_sample_replay_buffer_indices()

        # Using list comprehension to sample from replay buffer
        state_sample = np.array([self.state_history[i] for i in indices])
        state_next_sample = None #np.array([self.state_next_history[i] for i in indices])
        rewards_sample = [self.rewards_history[i] for i in indices]
        action_sample = [self.action_history[i] for i in indices]
        done_sample = tf.convert_to_tensor([float(self.done_history[i]) for i in indices])

        return state_sample, state_next_sample, rewards_sample, action_sample, done_sample

    def get_sample_replay_buffer_indices(self):
        return np.random.choice(range(len(self.done_history)), size=self.sample_size)

    def calculate_updated_q_values(self, state_next_sample, rewards_sample, done_sample):
        updated_q_values = rewards_sample
        # If final frame set the last value to -1
        updated_q_values = updated_q_values * (1 - done_sample) - done_sample
        return updated_q_values

    def delete_old_replay_buffer_values(self):
        # Limit the state and reward history
        if len(self.rewards_history) > self.max_replay_buffer_length:
            del self.rewards_history[:1]
            del self.state_history[:1]
            # del self.state_next_history[:1]
            del self.action_history[:1]
            del self.done_history[:1]

    def get_mean_reward(self):
        if self.episode_count > 0:
            return np.mean(self.episode_reward_history[-self.reward_history_limit:])
        else:
            return 0.0

    def solved(self, mean_reward):
        if mean_reward > self.solved_mean_reward:  # Condition to consider the task solved
            print("Solved at episode {}!".format(self.episode_count))
            return True
        else:
            return False

    def play(self):
        global keyboard_input
        keyboard_input = [False for _ in range(self.simulation_manager.number_of_possible_actions)]

        def on_press(key):
            global keyboard_input
            keyboard_input[int(key.char)-1] = True

        def on_release(key):
            global keyboard_input
            keyboard_input[int(key.char)-1] = False


        with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
            self.simulation_manager.reset()
            action_index = 4
            episode_reward = 0
            episode_steps = 0

            while True:
                episode_steps += 1

                # Select an action
                if True in keyboard_input:
                    action_index = keyboard_input.index(True)

                episode_reward += self.step(action_index, td=False)

                if self.end_episode(episode_reward, episode_steps):
                    break

            listener.join()

    def random(self):
        episode = 1
        for episode in range(1, episode + 1):
            # Reset the environment
            self.simulation_manager.reset()
            episode_reward = 0
            episode_steps = 0

            action_table = self.simulation_manager.action_table
            print(action_table)
            action = 5
            # Run steps in episode
            while True:
                # Increment the total number of steps taken by the AI in total.
                episode_steps += 1

                if episode_steps in [40, 120, 200, 280]:
                    action = 6
                elif episode_steps in [80, 160, 240, 320]:
                    action = 2
                else:
                    action = 4

                # legal_actions = self.simulation_manager.get_legal_actions()
                # if len(legal_actions) == 1:
                #     self.step(legal_actions[0], td=False)
                #     continue

                # TODO: Comment out td decision making if td=True
                reward = self.step(action, td=True)

                if episode_steps in [40, 120, 200, 280]:
                    print(action_table[action], " - ", reward)
                elif episode_steps in [80, 160, 240, 320]:
                    print(action_table[action], " - ", reward)

                episode_reward += reward

                if self.end_episode(episode_reward, episode_steps):
                    break
                #
                sys.stdout.write("\rstep: {0} / reward: {1}".format(str(episode_steps), str(episode_reward)))
                sys.stdout.flush()

        return str(episode)

    def save_model_weights(self, file_location, save_name):
        if os.path.isdir(file_location + "/" + save_name):
            os.mkdir(file_location + "/" + save_name)
        self.ml_model.save_weights(file_location + "/" + save_name)

    def save_model(self,file_location, save_name):
        if os.path.isdir(file_location + "/" + save_name):
            os.mkdir(file_location + "/" + save_name)
        self.ml_model.save(file_location + "/" + save_name)

    def load_weights(self, model, file_location, save_name):
        model.load_weights(file_location + "/" + save_name)
        return model

    def load_model(self, file_location, save_name):
        return keras.models.load_model(file_location + "/" + save_name)


if __name__ == "__main__":
    # Reference Files
    junction_file_path = os.path.join(os.path.dirname(os.path.join(os.path.dirname(os.path.join(os.path.dirname(__file__))))), "junctions", "scale_library_pub_junction.junc")
    configuration_file_path = os.path.join(os.path.dirname(os.path.join(os.path.dirname(os.path.join(os.path.dirname(__file__))))), "configurations", "simulation_config", "cross_road.config")

    # Settings
    scale = 30

    # Visualiser Init
    visualiser = JunctionVisualiser()
    visualiser_update_function = visualiser.update
    # visualiser_update_function = None
    # Simulation
    # simulation = SimulationManager(junction_file_path, configuration_file_path, visualiser_update_function)
    simulation = SimulationManager(junction_file_path, configuration_file_path, None)
    machine_learning = MachineLearning(simulation, machine_learning_config=None)
    #
    # machine_learning.random()
    machine_learning.train()
    # machine_learning.test()

    # # Visualiser Setup
    # visualiser.define_main(machine_learning.play)
    # visualiser.load_junction(junction_file_path)
    # visualiser.set_scale(scale)
    # #
    # # Run Simulation
    # visualiser.open()

