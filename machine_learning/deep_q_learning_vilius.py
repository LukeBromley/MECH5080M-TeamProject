from platform import system
if system() == 'Windows':
    import sys
    sys.path.append('./')

import os
from simulation.environment import Environment
from gui.junction_visualiser import JunctionVisualiser

import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

# https://towardsdatascience.com/a-minimal-working-example-for-deep-q-learning-in-tensorflow-2-0-e0ca8a944d5e


class MachineLearning:
    def __init__(self, junction_file_path, config_file_path, visualiser_update_function=None):
        self.environment = Environment(junction_file_path, config_file_path, visualiser_update_function)

        # COUNTERS
        self.episode_count = 0
        self.number_of_steps_taken = 0  # number of ticks seen over entire training

        # TRAINING LIMITS
        self.max_steps_per_episode = 100000
        self.solved_mean_reward = 100000

        # TAKING AN ACTION
        # Actions
        self.number_of_possible_actions = 3

        # Random action
        self.random_action_selection_probabilities = [0.9, 0.05, 0.05]
        assert len(self.random_action_selection_probabilities) == self.number_of_possible_actions

        # Probability of selecting a random action
        self.epsilon_greedy_min = 0.1  # Minimum epsilon greedy parameter
        self.epsilon_greedy_max = 1.0  # Maximum epsilon greedy parameter
        self.epsilon_greedy = self.epsilon_greedy_max  # Epsilon greedy parameter

        # Exploration
        self.number_of_steps_of_required_exploration = 1000  # 10000
        self.number_of_steps_of_exploration_reduction = 5000  # 50000

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
        self.learning_rate = 0.01  # 0.00025
        self.optimizer = keras.optimizers.legacy.Adam(learning_rate=self.learning_rate, clipnorm=1.0)

        # OTHER

        # Train the model after 4 actions
        self.update_after_actions = 10

        # How often to update the target network
        self.update_target_network = 10000

        # Using huber loss for stability
        self.loss_function = keras.losses.Huber()

        # Experience replay buffers

        # The first model makes the predictions for Q-values which are used to
        # make a action.
        self.model = self.create_q_model()
        # Build a target model for the prediction of future rewards.
        # The weights of a target model get updated every 10000 steps thus when the
        # loss between the Q-values is calculated the target Q-value is stable.
        self.model_target = self.create_q_model()

    def create_q_model(self):
        inputs = tf.keras.layers.Input(shape=(10,))
        layer = layers.Dense(512, activation="relu")(inputs)
        outputs = tf.keras.layers.Dense(self.number_of_possible_actions, activation='linear')(layer)
        return tf.keras.models.Model(inputs=inputs, outputs=outputs)

    def train(self):
        while True:  # Run until solved
            state = np.array(self.environment.reset())
            episode_reward = 0
            mean_reward = 0

            for step in range(1, self.max_steps_per_episode):

                # Increment the total number of steps taken by the AI in total.
                self.number_of_steps_taken += 1

                # Select an action
                action = self.select_action(state)

                # Take an action
                next_state, reward, done = self.take_step(action)

                # Update reward
                episode_reward += reward

                # Save actions and states in replay buffer
                self.save_to_replay_buffers(action, state, next_state, done, reward)

                # Update State
                state = next_state

                # Update every fourth frame and once batch size is over 32
                if self.number_of_steps_taken % self.update_after_actions == 0 and len(self.done_history) > self.sample_size:

                    state_sample, state_next_sample, rewards_sample, action_sample, done_sample = self.sample_replay_buffers()

                    updated_q_values = self.calculate_updated_q_values(state_next_sample, rewards_sample, done_sample)

                    with tf.GradientTape() as tape:
                        # Train the model on the states and updated Q-values
                        q_values = self.model(state_sample)

                        # Apply the masks to the Q-values to get the Q-value for action taken
                        # Create a mask so we only calculate loss on the updated Q-values
                        masks = tf.one_hot(action_sample, self.number_of_possible_actions)
                        q_action = tf.reduce_sum(tf.multiply(q_values, masks), axis=1)

                        # Calculate loss between new Q-value and old Q-value
                        loss = self.loss_function(updated_q_values, q_action)

                    # Backpropagation
                    grads = tape.gradient(loss, self.model.trainable_variables)
                    self.optimizer.apply_gradients(zip(grads, self.model.trainable_variables))

                if self.number_of_steps_taken % self.update_target_network == 0:
                    # update the the target network with new weights
                    self.model_target.set_weights(self.model.get_weights())
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
        return np.random.choice(self.number_of_possible_actions, p=self.random_action_selection_probabilities)

    def select_best_action(self, state):
        # Predict action Q-values
        # From environment state
        state_tensor = tf.expand_dims(tf.convert_to_tensor(state), 0)
        action_probs = self.model(state_tensor, training=False)
        # Take best action
        action = tf.argmax(action_probs[0]).numpy()
        return action

    def update_epsilon_greedy(self):
        self.epsilon_greedy -= (self.epsilon_greedy_max - self.epsilon_greedy_min) / self.number_of_steps_of_exploration_reduction
        self.epsilon_greedy = max(self.epsilon_greedy, self.epsilon_greedy_min)

    def take_step(self, action):
        state_next, reward, done = self.environment.take_step(action)
        state_next = np.array(state_next)
        return state_next, reward, done

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
        future_rewards = self.model_target.predict(state_next_sample, verbose=0)
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
            self.environment.reset()
            done = False
            score = 0
            steps = 0
            while not done:
                steps += 1
                action_index = self.environment.action_space.sample()
                n_state, reward, done = self.environment.take_step(action_index)
                score += reward
            print(f"Episode: {episode} Score: {score} Steps: {steps}")


if __name__ == "__main__":
    # Reference Files
    junction_file_path = os.path.join(os.path.dirname(os.path.join(os.path.dirname(__file__))), "junctions", "cross_road.junc")
    configuration_file_path = os.path.join(os.path.dirname(os.path.join(os.path.dirname(__file__))), "configurations", "cross_road.config")

    # # Settings
    # scale = 100
    #
    # # Visualiser Init
    # visualiser = JunctionVisualiser()

    # Simulation
    machine_learning = MachineLearning(junction_file_path, configuration_file_path)

    # machine_learning.random()
    machine_learning.train()

    # # Visualiser Setup
    # visualiser.define_main(machine_learning.train)
    # visualiser.load_junction(junction_file_path)
    # visualiser.set_scale(scale)
    #
    # # Run Simulation
    # visualiser.open()

