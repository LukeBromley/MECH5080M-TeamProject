from platform import system
if system() == 'Windows':
    import sys
    sys.path.append('./')

import os
from simulation.environment import SimulationManager
from gui.junction_visualiser import JunctionVisualiser
from time import sleep

import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

# https://towardsdatascience.com/a-minimal-working-example-for-deep-q-learning-in-tensorflow-2-0-e0ca8a944d5e


class MachineLearning:
    def __init__(self, junction_file_path, simulation_config_file_path, machine_learning_config, visualiser_update_function=None):
        # SIMULATION MANAGER
        self.simulation_manager = SimulationManager(junction_file_path, simulation_config_file_path, visualiser_update_function)

        # COUNTERS
        self.episode_count = 0  # Number of episodes trained
        self.number_of_steps_taken = 0  # Total number of steps taken over all episodes
        self.all_time_reward = 0  # Total reward over all episodes

        # TRAINING LIMITS
        self.max_steps_per_episode = 100000  # Maximum number of steps allowed per episode
        self.episode_end_reward = -500000  # Single episode total reward minimum threshold to end episode
        self.solved_mean_reward = 100000  # Single episode total reward minimum threshold to consider ML trained

        # TAKING AN ACTION
        # Random action
        self.random_action_do_nothing_probability = 0.9
        self.random_action_selection_probabilities = [self.random_action_do_nothing_probability]
        for action_index in range(1, self.simulation_manager.number_of_possible_actions):
            self.random_action_selection_probabilities.append((1 - self.random_action_do_nothing_probability) / (self.simulation_manager.number_of_possible_actions - 1))
        assert len(self.random_action_selection_probabilities) == self.simulation_manager.number_of_possible_actions

        # Probability of selecting a random action
        self.epsilon_greedy_min = 0.1  # Minimum probability of selecting a random action
        self.epsilon_greedy_max = 1.0  # Maximum probability of selecting a random action
        self.epsilon_greedy = self.epsilon_greedy_max  # Current probability of selecting a random action

        # Exploration
        self.number_of_steps_of_required_exploration = 1000  # 10000  # Number of steps of just random actions before the network can make some decisions
        self.number_of_steps_of_exploration_reduction = 5000  # 50000 # Number of steps over which epsilon greedy decays

        # REPLAY
        # Buffers
        self.action_history = []
        self.state_history = []
        self.state_next_history = []
        self.rewards_history = []
        self.done_history = []
        self.episode_reward_history = []

        # Sample Size
        self.sample_size = 32  # Size of batch taken from replay buffer

        # Discount factor
        self.gamma = 0.9  # Discount factor for past rewards

        # Maximum replay buffer length
        # Note: The Deepmind paper suggests 1000000 however this causes memory issues
        self.max_replay_buffer_length = 100000

        # OPTIMISING
        # Note: In the Deepmind paper they use RMSProp however then Adam optimizer
        self.learning_rate = 0.00001  # 0.00025
        self.optimizer = keras.optimizers.legacy.Adam(learning_rate=self.learning_rate, clipnorm=1.0)

        # OTHER

        # Train the model after 4 actions
        self.update_after_actions = 10

        # How often to update the target network
        self.update_target_network = 10000

        # Using huber loss for stability
        self.loss_function = keras.losses.Huber()

        # MACHINE LEARNING MODELS
        self.ml_model_hidden_layers = [512]

        self.ml_model = self.create_q_learning_model(self.simulation_manager.observation_space_size, self.simulation_manager.number_of_possible_actions, self.ml_model_hidden_layers)  # Makes the predictions for Q-values which are used to make a action.
        self.ml_model_target = self.create_q_learning_model(self.simulation_manager.observation_space_size, self.simulation_manager.number_of_possible_actions, self.ml_model_hidden_layers)  # For the prediction of future rewards. The weights of a target model get updated every 10000 steps thus when the loss between the Q-values is calculated the target Q-value is stable.

    def create_q_learning_model(self, state_size, action_size, hidden_layers):
        ml_layers = [layers.Input(shape=(state_size, ))]  # input dimension
        for number_of_perceptrons in hidden_layers:
            ml_layers.append(layers.Dense(number_of_perceptrons, activation="relu")(ml_layers[-1]))
        q_values = layers.Dense(action_size, activation="linear")(ml_layers[-1])
        q_network = tf.keras.models.Model(inputs=ml_layers[0], outputs=[q_values])
        return q_network

    def train(self):
        while True:  # Run until solved
            state = np.array(self.simulation_manager.reset())
            episode_reward = 0
            mean_reward = 0

            # Run steps in episode
            for step in range(1, self.max_steps_per_episode):

                # Increment the total number of steps taken by the AI in total.
                self.number_of_steps_taken += 1

                # Select an action
                action_index = self.select_action(state)

                # Take an action
                action_penalty = self.take_action(action_index)

                # Run simulation 1 step
                self.step_simulation()

                # Compute metrics used to get state and calculate reward
                self.compute_simulation_metrics()

                # Calculate reward
                reward = self.calculate_reward(action_penalty, step)

                # Update reward
                self.all_time_reward += reward
                episode_reward += reward

                # Determine if episode is over
                done = self.end_episode(episode_reward, step)

                # Get the next state
                next_state = self.get_state()

                # Save actions and states in replay buffer
                self.save_to_replay_buffers(action_index, state, next_state, done, reward)

                # Update State
                state = next_state

                # Update every fourth frame and once batch size is over 32
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
                    # update the the target network with new weights
                    self.ml_model_target.set_weights(self.ml_model.get_weights())
                    # Log details
                    template = "running reward: {:.2f} at episode {}, frame count {}"
                    print(template.format(mean_reward, self.episode_count, self.number_of_steps_taken))

                # Delete old buffer values
                self.delete_old_replay_buffer_values()

                if done:
                    break

            mean_reward = self.get_mean_reward(episode_reward)

            self.episode_count += 1

            if self.solved(mean_reward):
                break

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


    def compute_simulation_metrics(self):
        self.simulation_manager.compute_simulation_metrics()

    def calculate_reward(self, action_penalty, iteration):
        return self.simulation_manager.calculate_reward(action_penalty, iteration)

    def end_episode(self, episode_reward, step):
        if episode_reward < self.episode_end_reward:
            print("Score at episode end:", episode_reward, "/ Steps:", step)
            return True
        else:
            return False

    def get_state(self):
        state_next = np.asarray(self.simulation_manager.get_state()).astype('float32')
        return np.array(state_next)

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

    def get_mean_reward(self, episode_reward):
        self.save_reward_history(episode_reward)
        self.delete_old_reward_history()
        return np.mean(self.episode_reward_history)

    def save_reward_history(self, episode_reward):
        self.episode_reward_history.append(episode_reward)

    def delete_old_reward_history(self):
        if len(self.episode_reward_history) > 100:
            del self.episode_reward_history[:1]

    def solved(self, mean_reward):
        if mean_reward > self.solved_mean_reward:  # Condition to consider the task solved
            print("Solved at episode {}!".format(self.episode_count))
            return True
        else:
            return False

    def random(self):
        episode = 5
        for episode in range(1, episode + 1):
            self.simulation_manager.reset()

            episode_reward = 0
            # Run steps in episode
            for step in range(1, self.max_steps_per_episode):

                # Increment the total number of steps taken by the AI in total.
                self.number_of_steps_taken += 1

                # Select an action
                action_index = self.select_random_action()

                # Take an action
                action_penalty = self.take_action(0)

                # Run simulation 1 step
                self.step_simulation(visualiser_on=True, visualiser_sleep_time=0.01)

                # Compute metrics used to get state and calculate reward
                self.compute_simulation_metrics()

                # Calculate reward
                reward = self.calculate_reward(action_penalty, step)

                # Update reward
                self.all_time_reward += reward
                episode_reward += reward

                # Determine if episode is over
                if self.end_episode(episode_reward, step):
                    break


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

    # machine_learning.random()
    # machine_learning.train()

    # Visualiser Setup
    visualiser.define_main(machine_learning.random)
    visualiser.load_junction(junction_file_path)
    visualiser.set_scale(scale)

    # Run Simulation
    visualiser.open()

