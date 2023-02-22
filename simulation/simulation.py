from platform import system
if system() == 'Windows':
    import sys
    sys.path.append('./')

from time import sleep
from gui.junction_visualiser import JunctionVisualiser
from library.model import Model
from library.vehicles import Vehicle
from library.maths import calculate_rectangle_corner_coords, calculate_range_overlap, calculate_line_gradient_and_constant, clamp
import os
from functools import partial


class Simulation:
    def __init__(self, junction_file_path: str, config_file_path, visualiser_update_function = None):
        self.uid = 0

        # Model
        self.model = Model()
        self.model.load_junction(junction_file_path)
        self.model.generate_routes()
        self.model.load_config(config_file_path)
        self.vehicle_data = []
        self.collision = False

        # Visualiser
        self.visualiser_update_function = visualiser_update_function

    def run_continuous(self, speed_multiplier=None):
        for tick in range(self.model.config.simulation_duration):
            self.run_single_iteration()
            if speed_multiplier is not None:
                sleep(self.model.tick_time / speed_multiplier)

    def run_single_iteration(self):
        self.compute_single_iteration()

        # Update visualiser
        if self.visualiser_update_function is not None:
            self.visualiser_update_function(self.vehicle_data, self.model.lights, self.model.calculate_time_of_day(), self.collision)

    def compute_single_iteration(self):
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
        self.vehicle_data = []
        for vehicle in self.model.vehicles:
            coord_x, coord_y = self.model.get_vehicle_coordinates(vehicle.uid)
            angle = self.model.get_vehicle_direction(vehicle.uid)

            object_ahead, delta_distance_ahead = self.model.get_object_ahead(vehicle.uid)
            vehicle.update(self.model.tick_time, object_ahead, delta_distance_ahead)
            vehicle.update_position_data([coord_x, coord_y])

            self.vehicle_data.append([coord_x, coord_y, angle, vehicle.length, vehicle.width, vehicle.uid])

        collision = self.check_colision(self.vehicle_data)
        self.collision = True if collision is not None else False

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
    simulation = Simulation(junction_file_path, configuration_file_path, visualiser.update)

    # Visualiser Setup
    visualiser.define_main(partial(simulation.run_continuous, speed_multiplier))
    visualiser.load_junction(junction_file_path)
    visualiser.set_scale(scale)

    # Run Simulation
    visualiser.open()

