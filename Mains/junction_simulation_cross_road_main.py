from platform import system
if system() == 'Windows':
    import sys
    sys.path.append('./')

from time import sleep
from Frontend.JunctionVisualiser import JunctionVisualiser
from Library.model import Model
from Library.vehicles import Vehicle
from Library.environment import Time
from Library.maths import calculate_rectangle_corner_coords, calculate_range_overlap, calculate_line_gradient_and_constant, clamp
from config import ROOT_DIR
import os


class Simulation:
    def __init__(self, junction_file_path: str, config_file_path):
        self.uid = 0

        # Model
        self.model = Model()
        self.model.load_junction(junction_file_path)
        self.model.load_config(config_file_path)
        self.model.generate_routes()

        # Override Spawning system
        self.model.setup_fixed_spawning(2)

        # Visualiser
        self.visualiser = JunctionVisualiser()
        self.visualiser.define_main(self.main)
        self.visualiser.load_junction(junction_file_path)
        self.visualiser.set_scale(self.model.config.visualiser_scale)

        # Light init
        self.model.set_state(1, colour='red')

        # Collision State
        self.collision = False

    def tick(self):
        # Spawn vehicles
        for index, node_uid in enumerate(self.model.calculate_start_nodes()):
            nudge_result = self.model.nudge_spawner(node_uid, self.model.calculate_time_of_day())
            if nudge_result is not None:
                route_uid, length, width, distance_delta = nudge_result
                self.add_vehicle(route_uid, length, width, distance_delta)

        # Control lights
        for light in self.model.get_lights():
            light.update(self.model.tick_time)

        # Remove finished vehicles
        self.model.remove_finished_vehicles()

        # Update vehicle position
        coordinates = []
        coordinates_angle_size = []
        for vehicle in self.model.vehicles:
            coord_x, coord_y = self.model.get_vehicle_coordinates(vehicle.uid)
            angle = self.model.get_vehicle_direction(vehicle.uid)

            object_ahead, delta_distance_ahead = self.model.get_object_ahead(vehicle.uid)
            vehicle.update(self.model.tick_time, object_ahead, delta_distance_ahead)
            vehicle.update_position_data([coord_x, coord_y])

            coordinates.append([coord_x, coord_y])
            coordinates_angle_size.append([coord_x, coord_y, angle, vehicle.length, vehicle.width, vehicle.uid])

        collision = self.check_colision(coordinates_angle_size)
        self.collision = True if collision is not None else False

        # Update visualiser
        self.visualiser.update_vehicle_positions(coordinates_angle_size)
        self.visualiser.update_light_colours(self.model.lights)
        self.visualiser.update_time(self.model.calculate_time_of_day())
        self.visualiser.update_collision_warning(self.collision)

        # Increment Time
        self.model.tock()

    def add_vehicle(self, route_uid: int, length, width, didstance_delta):
        self.uid += 1
        self.model.add_vehicle(
            Vehicle(
                uid=self.uid,
                start_time=self.model.calculate_seconds_elapsed(),
                route_uid=route_uid,
                speed=self.model.config.initial_speed,
                acceleration=self.model.config.initial_acceleration,
                maximum_acceleration=self.model.config.maximum_acceleration,
                maximum_deceleration=self.model.config.maximum_deceleration,
                preferred_time_gap=self.model.config.preferred_time_gap,
                maximum_speed=self.model.config.maximum_speed,
                length=length,
                width=width,
                min_creep_distance=self.model.config.min_creep_distance
            )
        )

    def check_colision(self, all_vehicle_parameters: [[int, int, int, int, int, int]]):
        lines = []
        for vehicle_parameters in all_vehicle_parameters:
            x, y, a, l, w, uid = vehicle_parameters
            xy1, xy2, xy3, xy4 = calculate_rectangle_corner_coords(
                x, y, a, l, w)
            lines.append([xy1, xy2, uid])
            lines.append([xy2, xy3, uid])
            lines.append([xy3, xy4, uid])
            lines.append([xy4, xy1, uid])

        for i in range(len(lines)):
            x1_1, y1_1, x1_2, y1_2 = lines[i][0][0], lines[i][0][1], lines[i][1][0], lines[i][1][1]
            uid1 = lines[i][2]
            for j in range(i + 1, len(lines)):
                x2_1, y2_1, x2_2, y2_2 = lines[j][0][0], lines[j][0][1], lines[j][1][0], lines[j][1][1]
                uid2 = lines[j][2]
                if uid1 == uid2:
                    continue

                if x1_1 == x1_2 and x2_1 == x2_2:  # if line 1 and line 2 is vertical
                    if x1_1 == x2_1:  # If line 1 and lin 2 are both on the same x value
                        # Check if they overlap in the y direction
                        y1_min = min(y1_1, y1_2)
                        y1_max = max(y1_1, y1_2)
                        y2_min = min(y2_1, y2_2)
                        y2_max = max(y2_1, y2_2)
                        overlap_range = calculate_range_overlap(
                            y1_min, y1_max, y2_min, y2_max)
                        if overlap_range is None:
                            continue
                        else:
                            return uid1, uid2
                    else:
                        continue

                elif x1_1 == x1_2:  # if line 1 is vertical
                    if min(x2_1, x2_2) <= x1_1 <= max(x2_1, x2_2):
                        m, c = calculate_line_gradient_and_constant(
                            x2_1, y2_1, x2_2, y2_2)
                        y = m * x1_1 + c
                        if min(y1_1, y1_2) <= y <= max(y1_1, y1_2):
                            return uid1, uid2
                        else:
                            continue
                    else:
                        continue

                elif x2_1 == x2_2:  # if line 2 is vertical
                    if min(x1_1, x1_2) <= x2_1 <= max(x1_1, x1_2):
                        m, c = calculate_line_gradient_and_constant(
                            x1_1, y1_1, x1_2, y1_2)
                        y = m * x2_1 + c
                        if min(y2_1, y2_2) <= y <= max(y2_1, y2_2):
                            return uid1, uid2
                        else:
                            continue
                    else:
                        continue

                else:
                    m1, c1 = calculate_line_gradient_and_constant(
                        x1_1, y1_1, x1_2, y1_2)
                    m2, c2 = calculate_line_gradient_and_constant(
                        x2_1, y2_1, x2_2, y2_2)

                    if m1 == m2 and c1 == c2:  # if they have the same gradient and intersection point
                        x1_min = min(x1_1, x1_2)
                        x1_max = max(x1_1, x1_2)
                        x2_min = min(x2_1, x2_2)
                        x2_max = max(x2_1, x2_2)
                        overlap_range = calculate_range_overlap(
                            x1_min, x1_max, x2_min, x2_max)
                        if overlap_range is None:
                            continue
                        else:
                            return uid1, uid2

                    # if they have the same gradient (but different intersection point)
                    elif m1 == m2:
                        continue
                    else:
                        x1_min = min(x1_1, x1_2)
                        x1_max = max(x1_1, x1_2)
                        x2_min = min(x2_1, x2_2)
                        x2_max = max(x2_1, x2_2)
                        overlap_range = calculate_range_overlap(
                            x1_min, x1_max, x2_min, x2_max)
                        if overlap_range is None:
                            continue
                        else:
                            x_cross = (c2 - c1) / (m1 - m2)
                            if overlap_range[0] <= x_cross <= overlap_range[1]:
                                return uid1, uid2
                            else:
                                continue
        return None


from tensorflow import keras, GradientTape, stop_gradient
from keras import layers, initializers
import numpy as np

# https://towardsdatascience.com/a-minimal-working-example-for-deep-q-learning-in-tensorflow-2-0-e0ca8a944d5e


class MachineLearning:
    def __init__(self):
        self.simulation = None

        self.max_number_of_vehicles = 10
        self.stats_per_vehicle = 4
        self.number_of_episodes = 10000
        self.exploration_rate = 0.1  # Exploration rate
        self.learning_rate = 0.01  # LEarning rate

        self.actions = [1, 2, 3, 4]
        self.action_space_size = len(self.actions)

        self.network = self.construct_q_learning_netowrk(self.max_number_of_vehicles, self.stats_per_vehicle, self.action_space_size)

        self.reset()

    def reset(self):
        self.simulation = Simulation(
            os.path.join(ROOT_DIR, "Junction_Designs", "cross_road.junc"),
            os.path.join(ROOT_DIR, "Junction_Designs", "blank_config.config")
        )
        self.simulation.visualiser.open()

    def construct_q_learning_netowrk(self, state_dim_width, state_dim_height, action_dim):
        inputs = layers.Input(shape=(state_dim_width, state_dim_height))  # input dimension
        hidden1 = layers.Dense(25, activation="relu", kernel_initializer=initializers.he_normal())(inputs)
        hidden2 = layers.Dense(25, activation="relu", kernel_initializer=initializers.he_normal())(hidden1)
        hidden3 = layers.Dense(25, activation="relu", kernel_initializer=initializers.he_normal())(hidden2)
        q_values = layers.Dense(action_dim, kernel_initializer=initializers.Zeros(), activation="linear")(hidden3)

        q_network = keras.Model(inputs=inputs, outputs=[q_values])
        return q_network

    def run(self):
        opt = keras.optimizers.Adam(learning_rate=self.learning_rate)

        for episode in range(self.number_of_episodes):
            with GradientTape() as tape:
                # Obtain Q-values from network
                # Essentially: Get the data from the simulation and give it to the neural netowrk
                q_values = self.network(self.get_state())

                # Select action using epsilon-greedy policy
                # Essentially: Gets a random value. if the value is less than the exploration rate then explore
                #              else get the prediction from the network
                sample_epsilon = np.random.rand()
                if sample_epsilon <= self.exploration_rate:  # Select random action
                    action = np.random.choice(self.actions)
                else:  # Select action with highest Q-value
                    action = np.argmax(q_values[0])

                "Obtain direct reward for selected action"
                reward = self.get_reward()  # get_reward(state, action)

                "Obtain Q-value for selected action"
                q_value = q_values[0, action]

                "Determine next state"
                next_state = get_state(state, action)

                "Select next action with highest Q-value"
                if next_state == terminal_state:
                    next_q_value = 0  # No Q-value for terminal
                else:
                    next_q_values = stop_gradient(self.network(next_state))  # No gradient computation
                    next_action = np.argmax(next_q_values[0])
                    next_q_value = next_q_values[0, next_action]

                "Compute observed Q-value"
                observed_q_value = reward + (self.learning_rate * next_q_value)

                "Compute loss value"
                loss_value = (observed_q_value - current_q_value) ** 2

                "Compute gradients"
                grads = tape.gradient(loss_value, self.network.trainable_variables)

                "Apply gradients to update network weights"
                opt.apply_gradients(zip(grads, self.network.trainable_variables))

                "Update state"
                state = next_state

    def machine_learning(self):
        data = self.get_state()
        # reward = self.get_reward()

    def get_state(self):
        data = []

        for vehicle in self.simulation.model.vehicles:
            speed = vehicle.get_speed()
            coordinates = self.simulation.model.get_vehicle_coordinates(vehicle.uid)
            data.append([speed, coordinates[0], coordinates[1], True])

        while len(data) < self.max_number_of_vehicles:
            data.append([0, 0, 0, False])

        return data

    def get_reward(self):
        crash_reward = -100
        wait_time_reward = -10

        total_reward = 0
        total_reward += crash_reward * 1 if self.simulation.collision else 0

        return total_reward


if __name__ == "__main__":
    machine_learning = MachineLearning()


# Reward / penalise


