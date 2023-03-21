import copy
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
    def __init__(self, simulation, machine_learning_config = None, graph_num_episodes=20, graph_max_step=30000):
        # SIMULATION MANAGER
        self.future_wait_time = None
        self.simulation_manager = simulation

        # GRAPH
        # self.graph = Graph(graph_num_episodes, graph_max_step)

        # COUNTERS
        self.episode_count = 0  # Number of episodes trained
        self.number_of_steps_taken = 0  # Total number of steps taken over all episodes
        self.all_time_reward = 0  # Total reward over all episodes

        # TRAINING LIMITS
        self.max_steps_per_episode = 10000  # Maximum number of steps allowed per episode
        self.episode_end_reward = -30  # Single episode total reward minimum threshold to end episode
        self.solved_mean_reward = 400  # Single episode total reward minimum threshold to consider ML trained
        self.reward_history_limit = 50

        # TAKING AN ACTION
        # Random action
        # self.random_action_selection_probabilities = [0.9, 0.025, 0.025, 0.025, 0.025]
        self.random_action_selection_probabilities = [0.01, 0.4, 0.4, 0.19]

        # Probability of selecting a random action
        self.epsilon_greedy_min = 0.01  # Minimum probability of selecting a random action
        self.epsilon_greedy_max = 0.95  # Maximum probability of selecting a random action
        self.epsilon_greedy = self.epsilon_greedy_max  # Current probability of selecting a random action

        # Exploration
        # Number of steps of just random actions before the network can make some decisions
        self.number_of_steps_of_required_exploration = 1000
        # Number of steps over which epsilon greedy decays
        self.number_of_steps_of_exploration_reduction = 10000
        # Train the model after 4 actions
        self.update_after_actions = 10
        # How often to update the target network
        self.update_target_network = 1000

        # REPLAY
        # Buffers
        self.action_history = []
        self.state_history = []
        self.state_next_history = []
        self.rewards_history = []
        self.done_history = []
        self.episode_reward_history = []

        # Steps to look into the future to determine the mean reward. Should match T = 1/(1-gamma)

        self.seconds_to_look_into_the_future = 2.5
        self.steps_to_look_into_the_future = int(self.seconds_to_look_into_the_future / self.simulation_manager.simulation.model.tick_time)
        # Sample Size
        self.sample_size = 124  # Size of batch taken from replay buffer

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
        self.ml_model_hidden_layers = [512, 512]

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
    def reset(self):
        self.episode_count = 0  # Number of episodes trained
        self.number_of_steps_taken = 0  # Total number of steps taken over all episodes
        self.all_time_reward = 0  # Total reward over all episodes

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
            action_log = []

            # Run steps in episode
            while True:

                # Increment the total number of steps taken by the AI in total.
                self.number_of_steps_taken += 1

                # Increment the episode step
                episode_step += 1

                # Select an action
                action_index = self.select_action(state)
                action_log.append(action_index)
                # Take an action
                action_penalty = self.take_action(action_index)

                # Run simulation 1 step
                self.step_simulation()

                # Calculate reward
                # TODO: Reset the state if reward is low so the network can take another try
                reward = self.calculate_reward(action_penalty, predict=True)

                # Update reward
                self.all_time_reward += reward

                # Update episode reward
                episode_reward += reward

                # Determine if episode is over
                done = self.end_episode(episode_reward, episode_step)

                # Get the next state
                next_state = self.get_state()

                # Save actions and states in replay buffer
                self.save_to_replay_buffers(action_index, state, next_state, done, reward)

                # Update State
                state = next_state

                # Update
                if self.number_of_steps_taken % self.update_after_actions == 0 and len(self.done_history) > self.sample_size:

                    state_sample, state_next_sample, rewards_sample, action_sample, done_sample = self.sample_replay_buffers()

                    updated_q_values = self.calculate_updated_q_values(state_next_sample, rewards_sample, done_sample)

                    with tf.GradientTape() as tape:
                        # Train the model on the states and updated Q-values
                        q_values = self.ml_model(state_sample)

                        # Apply the masks to the Q-values to get the Q-value for action taken
                        # Create a mask so we only calculate loss on the updated Q-values
                        masks = tf.one_hot(action_sample, self.simulation_manager.number_of_possible_actions)
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
                    #template = " =============== running reward: {:.2f} at episode {}, frame count {} ================"
                    #print(template.format(self.get_mean_reward(), self.episode_count, self.number_of_steps_taken))

                # Delete old buffer values
                self.delete_old_replay_buffer_values()

                if done:
                    break

            # print(action_log)
            self.episode_reward_history.append(episode_step)
            self.episode_count += 1

            if self.solved(self.get_mean_reward()):
                self.ml_model_target.save("saved_model_new")
                break
        return self.get_mean_reward()

    def select_action(self, state):
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
        return np.random.choice(self.simulation_manager.number_of_possible_actions, p=self.random_action_selection_probabilities)

    def select_best_action(self, state):
        # Predict action Q-values
        # From simulation_manager state
        state_tensor = tf.expand_dims(tf.convert_to_tensor(state), 0)
        action_probs = self.ml_model(state_tensor, training=False)
        # Take best action
        action = tf.argmax(action_probs[0]).numpy()
        return action

    def update_epsilon_greedy(self):
        self.epsilon_greedy -= (self.epsilon_greedy_max - self.epsilon_greedy_min) / self.number_of_steps_of_exploration_reduction
        self.epsilon_greedy = max(self.epsilon_greedy, self.epsilon_greedy_min)

    def take_action(self, action_index):
        return self.simulation_manager.take_action(action_index)

    def step_simulation(self, num_steps=1, visualiser_on=False, visualiser_sleep_time: float = 0):
        for step in range(num_steps):
            if visualiser_on:
                self.simulation_manager.simulation.run_single_iteration()
                sleep(visualiser_sleep_time)
            else:
                self.simulation_manager.simulation.compute_single_iteration()
            self.simulation_manager.compute_simulation_metrics()

    def calculate_reward(self, action_penalty, predict: bool = True):
        # TODO: Uncomment
        action_penalty = 0
        if predict:
            simulation_manager_copy = copy.deepcopy(self.simulation_manager)
            future_rewards = [self.simulation_manager.calculate_reward()]

            for step in range(self.steps_to_look_into_the_future):
                simulation_manager_copy.simulation.compute_single_iteration()
                simulation_manager_copy.compute_simulation_metrics()
                future_rewards.append(simulation_manager_copy.calculate_reward())
            self.future_wait_time = simulation_manager_copy.get_mean_wait_time()
            wait_time_gradient = 10 * (simulation_manager_copy.get_mean_wait_time()**2 - self.simulation_manager.get_mean_wait_time()**2)
            # if wait_time_gradient > 0:
            #     wait_time_reward = -wait_time_gradient**2
            # else:
            #     wait_time_reward = wait_time_gradient**2
            future_rewards = -10 if min(future_rewards) < -9 else 0
            return future_rewards - action_penalty - wait_time_gradient / 1000 - 1/1000
        else:
            self.simulation_manager.compute_simulation_metrics()
            return self.simulation_manager.calculate_reward() - action_penalty

    def end_episode(self, episode_reward, step):
        if episode_reward < self.episode_end_reward or step > self.max_steps_per_episode:
            #print("Score at episode end:", episode_reward, "/ Steps:", step)
            sys.stdout.write("\rEpisode: {0} / Mean Reward: {1}".format(str(self.episode_count), str(self.get_mean_reward())))
            sys.stdout.flush()
            return True
        else:
            return False

    def get_state(self):
        return np.array(self.simulation_manager.get_state())

    def save_to_replay_buffers(self, action, state, next_state, done, reward):
        self.action_history.append(action)
        self.state_history.append(state)
        self.state_next_history.append(next_state)
        self.done_history.append(done)
        self.rewards_history.append(reward)

    def sample_replay_buffers(self):
        # Get indices of samples for replay buffers
        indices = self.get_sample_replay_buffer_indices()

        # Using list comprehension to sample from replay buffer
        state_sample = np.array([self.state_history[i] for i in indices])
        state_next_sample = np.array([self.state_next_history[i] for i in indices])
        rewards_sample = [self.rewards_history[i] for i in indices]
        action_sample = [self.action_history[i] for i in indices]
        done_sample = tf.convert_to_tensor([float(self.done_history[i]) for i in indices])

        return state_sample, state_next_sample, rewards_sample, action_sample, done_sample

    def get_sample_replay_buffer_indices(self):
        return np.random.choice(range(len(self.done_history)), size=self.sample_size)

    def calculate_updated_q_values(self, state_next_sample, rewards_sample, done_sample):
        # Build the updated Q-values for the sampled future states
        # Use the target model for stability
        future_rewards = self.ml_model_target.predict(state_next_sample, verbose=0)
        # Q value = reward + discount factor * expected future reward
        updated_q_values = rewards_sample + self.gamma * tf.reduce_max(future_rewards, axis=1)
        # If final frame set the last value to -1
        updated_q_values = updated_q_values * (1 - done_sample) - done_sample
        return updated_q_values

    def delete_old_replay_buffer_values(self):
        # Limit the state and reward history
        if len(self.rewards_history) > self.max_replay_buffer_length:
            del self.rewards_history[:1]
            del self.state_history[:1]
            del self.state_next_history[:1]
            del self.action_history[:1]
            del self.done_history[:1]

    def get_mean_reward(self):
        if self.episode_count > 0:
            return np.mean(self.episode_reward_history[-self.reward_history_limit:])
        else:
            return "Unavailable"

    def solved(self, mean_reward):
        if mean_reward > self.solved_mean_reward:  # Condition to consider the task solved
            print("Solved at episode {}!".format(self.episode_count))
            return True
        else:
            return False

    def play(self):
        global keyboard_input
        keyboard_input = [False for _ in range(4)]

        def on_press(key):
            global keyboard_input
            keyboard_input[int(key.char)-1] = True

        def on_release(key):
            global keyboard_input
            keyboard_input[int(key.char)-1] = False


        with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
            self.simulation_manager.reset()
            action_index = 3
            while True:
                self.number_of_steps_taken += 1

                # Select an action
                if True in keyboard_input:
                    action_index = keyboard_input.index(True)

                # Take an action
                action_penalty = self.take_action(action_index)

                # Run simulation 1 step
                self.step_simulation(visualiser_on=True, visualiser_sleep_time=0.05)

                # Update reward
                reward = self.calculate_reward(action_penalty, predict=False)
                self.all_time_reward += reward

                if self.end_episode(self.all_time_reward, self.number_of_steps_taken):
                    break

                sys.stdout.write("\rstep: {0} / reward: {1}".format(str(self.number_of_steps_taken), str(self.all_time_reward)))
                sys.stdout.flush()

            listener.join()

    def random(self):
        episode = 1
        for episode in range(1, episode + 1):
            # Reset the environment
            self.simulation_manager.reset()
            self.reset()

            action = 1
            previous_action = 1
            reward_log = []
            light_change_log = []
            # Run steps in episode
            while True:
                # Increment the total number of steps taken by the AI in total.
                self.number_of_steps_taken += 1

                # Select an action
                action_index = self.select_random_action()

                if self.number_of_steps_taken % 20 == 0:
                    if action in [1, 2]:
                        action = 3
                    else:
                        if previous_action == 1:
                            action = 2
                            previous_action = 2
                        else:
                            action = 1
                            previous_action = 1
                    light_change_log.append(self.number_of_steps_taken)

                action_penalty = self.take_action(action)

                # Run simulation 1 step
                self.step_simulation(visualiser_on=False, visualiser_sleep_time=0.0)

                # Calculate reward
                reward = self.calculate_reward(action_penalty, predict=True)
                reward_log.append(reward)

                # Update reward
                self.all_time_reward += reward

                # Determine if episode is over
                if self.end_episode(self.all_time_reward, self.number_of_steps_taken):
                    rewards = [reward for reward in reward_log if reward > -9]
                    #print(rewards)
                    #print(light_change_log)
                    #plt.plot(rewards)
                    #for timestamp in light_change_log:
                        #plt.axvline(timestamp, c='green')
                    #plt.show()
                    break

                sys.stdout.write("\rstep: {0} / reward: {1}".format(str(self.number_of_steps_taken), str(self.all_time_reward)))
                sys.stdout.flush()
        return str(self.all_time_reward)


    def test(self):
        model = keras.models.load_model('saved_model')
        episode = 10
        reward_log = []
        for episode in range(1, episode + 1):
            # Reset the environment
            self.simulation_manager.reset()
            self.reset()

            # Run steps in episode
            while True:
                # Increment the total number of steps taken by the AI in total.
                self.number_of_steps_taken += 1

                # Select an action
                action_index = np.argmax(model(self.get_state().reshape(1, -1)))

                # Take an action
                action_penalty = self.take_action(action_index)

                # Run simulation 1 step
                self.step_simulation(visualiser_on=True, visualiser_sleep_time=0.05)

                # Calculate reward
                # TODO: Add a probability of a collision instead of a binary collision reward
                reward = self.calculate_reward(action_penalty, predict=False)
                reward_log.append(reward)
                self.all_time_reward += reward

                # Determine if episode is over
                if self.end_episode(self.all_time_reward, self.number_of_steps_taken):
                    rewards = [reward for reward in reward_log if reward > -9]
                    plt.plot(rewards)
                    print(rewards)
                    break

                sys.stdout.write("\rstep: {0} / reward: {1}".format(str(self.number_of_steps_taken), str(self.all_time_reward)))
                sys.stdout.flush()

    def run(self):
        state = np.array(self.simulation_manager.reset())
        while True:
            # Increment the total number of steps taken by the AI in total.
            self.number_of_steps_taken += 1

            # Select an action
            action_index = self.select_best_action(state)

            # Take an action
            self.take_action(action_index)

            # Run simulation 1 step
            self.step_simulation()

            # Get the next state
            state = self.get_state()

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
    junction_file_path = os.path.join(os.path.dirname(os.path.join(os.path.dirname(os.path.join(os.path.dirname(__file__))))), "junctions", "cross_road.junc")
    configuration_file_path = os.path.join(os.path.dirname(os.path.join(os.path.dirname(os.path.join(os.path.dirname(__file__))))), "configurations", "simulation_config", "cross_road.config")

    # Settings
    scale = 30

    # Visualiser Init
    visualiser = JunctionVisualiser()
    visualiser_update_function = visualiser.update
    # visualiser_update_function = None
    # Simulation
    simulation = SimulationManager(junction_file_path, configuration_file_path, visualiser_update_function)
    machine_learning = MachineLearning(simulation, machine_learning_config=None)
    #
    # machine_learning.random()
    # machine_learning.train()
    # machine_learning.test()

    #

    # Visualiser Setup
    visualiser.define_main(machine_learning.random())
    visualiser.load_junction(junction_file_path)
    visualiser.set_scale(scale)
    #
    # Run Simulation
    visualiser.open()

