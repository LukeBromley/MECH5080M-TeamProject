from platform import system
if system() == 'Windows':
    import sys
    sys.path.append('./')

from time import sleep
from Frontend.JunctionVisualiser import JunctionVisualiser
from Library.model import Model
from Library.vehicles import Vehicle
from Library.environment import Spawning, Time
from Library.maths import calculate_rectangle_corner_coords, calculate_range_overlap, calculate_line_gradient_and_constant, clamp
from config import ROOT_DIR
import os

import matplotlib as plt


class Simulation:
    def __init__(self, file_path: str):
        self.time = 0.0
        self.uid = 0

        # Model
        self.model = Model()
        self.model.load_junction(file_path)
        self.model.generate_routes()

        # Time
        self.model.set_start_time_of_day(Time(12, 0, 0))
        self.model.set_tick_rate(100)

        # Spawning system
        self.model.set_random_seed(1)
        # self.model.setup_random_spawning()
        self.model.setup_fixed_spawning(2)

        # Lights
        self.model.add_light([2])
        self.model.set_state(1, colour='red')

        # Visualiser
        self.visualiser = JunctionVisualiser()
        self.visualiser.define_main(self.main)
        self.visualiser.load_junction(file_path)
        self.visualiser.set_scale(100)

        # Spawning system
        self.spawning = []
        for node_uid in self.model.calculate_start_nodes():
            self.spawning.append(
                Spawning(node_uid, self.model.start_time_of_day))

    def main(self):
        a = 0

        for i in range(8640000):  # 24 simulation hours

            # Current Time
            time = self.model.calculate_time_of_day()
            if i % 90000 == 0:
                # print the time every 15 simulation mins
                print(time)

            if i > 0:
                if i % 2000 == 0:
                    self.model.set_state(1, 'green')
                if i % 2500 == 0:
                    self.model.set_state(1, 'red')

            # Spawn vehicles
            for index, node_uid in enumerate(self.model.calculate_start_nodes()):
                if self.spawning[index].nudge(time):
                    route_uid = self.spawning[index].select_route(
                        self.model.get_routes_with_starting_node(node_uid))
                    length, width = self.spawning[index].get_random_vehicle_size(
                    )
                    self.add_vehicle(route_uid, length, width)

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

                object_ahead, delta_distance_ahead = self.model.get_object_ahead(
                    vehicle.uid)
                vehicle.update(self.model.tick_time,
                               object_ahead, delta_distance_ahead)
                vehicle.update_position_data([coord_x, coord_y])

                coordinates.append([coord_x, coord_y])
                coordinates_angle_size.append(
                    [coord_x, coord_y, angle, vehicle.length, vehicle.width, vehicle.uid])

            collision = self.check_colision(coordinates_angle_size)

            # Update visualiser
            self.visualiser.update_vehicle_positions(coordinates_angle_size)
            self.visualiser.update_light_colours(self.model.lights)
            self.visualiser.update_time(self.model.calculate_time_of_day())
            self.visualiser.update_collision_warning(
                True if collision is not None else False)

            # Increment Time
            self.model.tock()
            sleep(self.model.tick_time * 0.1)

    def run(self):
        self.visualiser.open()

    def add_vehicle(self, route_uid: int, length, width, didstance_delta):
        self.uid += 1
        speed = clamp(didstance_delta * 0.2, 0, 5)
        self.model.add_vehicle(
            Vehicle(
                uid=self.uid,
                start_time=self.time,
                route_uid=route_uid,
                speed=5.0,
                acceleration=0.0,
                maximum_acceleration=3.0,
                maximum_deceleration=9.0,
                preferred_time_gap=2.0,
                maximum_speed=30.0,
                length=length,
                width=width,
                min_creep_distance=1
            )
        )

    def check_colision(self, coordinates_angle_size: [[int, int, int, int, int, int]]):
        lines = []
        for coordinate_angle_size in coordinates_angle_size:
            x, y, a, l, w, uid = coordinate_angle_size
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
    sim = Simulation(os.path.join(
        ROOT_DIR, "Junction_Designs", "example_junction.junc"))
    sim.run()
