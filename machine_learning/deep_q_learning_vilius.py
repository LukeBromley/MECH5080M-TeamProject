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
        # self.states = self.environment.observation_space.shape
        # self.actions = self.environment.action_space.n
        # self.environment.reset()

        self.num_actions = 3

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
        outputs = tf.keras.layers.Dense(self.num_actions, activation='linear')(layer)
        return tf.keras.models.Model(inputs=inputs, outputs=outputs)

    def train(self):
        # Configuration paramaters for the whole setup
        seed = 42
        gamma = 0.9  # Discount factor for past rewards
        epsilon = 1.0  # Epsilon greedy parameter
        epsilon_min = 0.1  # Minimum epsilon greedy parameter
        epsilon_max = 1.0  # Maximum epsilon greedy parameter
        epsilon_interval = (
                epsilon_max - epsilon_min
        )  # Rate at which to reduce chance of random action being taken
        batch_size = 32  # Size of batch taken from replay buffer
        max_steps_per_episode = 100000

        ###### In the Deepmind paper they use RMSProp however then Adam optimizer
        # improves training time
        optimizer = keras.optimizers.legacy.Adam(learning_rate=0.00025, clipnorm=1.0)

        # Experience replay buffers
        action_history = []
        state_history = []
        state_next_history = []
        rewards_history = []
        done_history = []
        episode_reward_history = []
        running_reward = 0
        episode_count = 0
        frame_count = 0 # number of ticks seen over entire training

        # Number of frames to take random action and observe output
        epsilon_random_frames = 10000

        # Number of frames for exploration
        epsilon_greedy_frames = 50000

        # Maximum replay length
        # Note: The Deepmind paper suggests 1000000 however this causes memory issues
        max_memory_length = 100000

        # Train the model after 4 actions
        update_after_actions = 10

        # How often to update the target network
        update_target_network = 10000

        # Using huber loss for stability
        loss_function = keras.losses.Huber()

        while True:  # Run until solved
            state = np.array(self.environment.reset())
            episode_reward = 0

            for timestep in range(1, max_steps_per_episode):
                # env.render(); Adding this line would show the attempts
                # of the agent in a pop up window.
                frame_count += 1

                # Use epsilon-greedy for exploration
                if frame_count < epsilon_random_frames or epsilon > np.random.rand(1)[0]:
                    # Take random action
                    action = np.random.choice(self.num_actions, p=[0.9, 0.05, 0.05])
                else:
                    # Predict action Q-values
                    # From environment state
                    state_tensor = tf.convert_to_tensor(state)
                    state_tensor = tf.expand_dims(state_tensor, 0)
                    action_probs = self.model(state_tensor, training=False)
                    # Take best action
                    action = tf.argmax(action_probs[0]).numpy()

                # Decay probability of taking random action
                epsilon -= epsilon_interval / epsilon_greedy_frames
                epsilon = max(epsilon, epsilon_min)

                # Apply the sampled action in our environment
                state_next, reward, done = self.environment.take_step(action)
                state_next = np.array(state_next)
                episode_reward += reward

                # Save actions and states in replay buffer
                action_history.append(action)
                state_history.append(state)
                state_next_history.append(state_next)
                done_history.append(done)
                rewards_history.append(reward)
                state = state_next

                # Update every fourth frame and once batch size is over 32
                if frame_count % update_after_actions == 0 and len(done_history) > batch_size:
                    # Get indices of samples for replay buffers
                    indices = np.random.choice(range(len(done_history)), size=batch_size)

                    # Using list comprehension to sample from replay buffer
                    # state_sample = np.array([state_history[i] for i in indices], dtype=object)
                    state_sample = np.array([state_history[i] for i in indices])
                    state_next_sample = np.array([state_next_history[i] for i in indices])
                    rewards_sample = [rewards_history[i] for i in indices]
                    action_sample = [action_history[i] for i in indices]
                    done_sample = tf.convert_to_tensor(
                        [float(done_history[i]) for i in indices]
                    )

                    # Build the updated Q-values for the sampled future states
                    # Use the target model for stability
                    future_rewards = self.model_target.predict(state_next_sample, verbose=0)
                    # Q value = reward + discount factor * expected future reward
                    updated_q_values = rewards_sample + gamma * tf.reduce_max(
                        future_rewards, axis=1
                    )

                    # If final frame set the last value to -1
                    updated_q_values = updated_q_values * (1 - done_sample) - done_sample

                    # Create a mask so we only calculate loss on the updated Q-values
                    masks = tf.one_hot(action_sample, self.num_actions)

                    with tf.GradientTape() as tape:
                        # Train the model on the states and updated Q-values
                        q_values = self.model(state_sample)

                        # Apply the masks to the Q-values to get the Q-value for action taken
                        q_action = tf.reduce_sum(tf.multiply(q_values, masks), axis=1)
                        # Calculate loss between new Q-value and old Q-value
                        loss = loss_function(updated_q_values, q_action)

                    # Backpropagation
                    grads = tape.gradient(loss, self.model.trainable_variables)
                    optimizer.apply_gradients(zip(grads, self.model.trainable_variables))

                if frame_count % update_target_network == 0:
                    # update the the target network with new weights
                    self.model_target.set_weights(self.model.get_weights())
                    # Log details
                    template = "running reward: {:.2f} at episode {}, frame count {}"
                    print(template.format(running_reward, episode_count, frame_count))

                # Limit the state and reward history
                if len(rewards_history) > max_memory_length:
                    del rewards_history[:1]
                    del state_history[:1]
                    del state_next_history[:1]
                    del action_history[:1]
                    del done_history[:1]

                if done:
                    break

            # Update running reward to check condition for solving
            episode_reward_history.append(episode_reward)
            if len(episode_reward_history) > 100:
                del episode_reward_history[:1]
            running_reward = np.mean(episode_reward_history)

            episode_count += 1

            if running_reward > 100000:  # Condition to consider the task solved
                print("Solved at episode {}!".format(episode_count))
                break

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

