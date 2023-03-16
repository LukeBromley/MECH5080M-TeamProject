from library.infrastructure import Route, TrafficLight
from library.maths import clamp
from math import sqrt
from typing import List


class Vehicle:
    def __init__(self, route_uid: int, start_time: float = 0.0, uid: int = 0,
                 speed: float = 0.0, acceleration: float = 0.0,
                 direction: float = 0.0, sensing_radius: float = 0.0,
                 maximum_acceleration: float = 1.5, maximum_deceleration: float = 2.0,
                 maximum_speed: float = 30.0, minimum_speed: float = 0.0,
                 distance_travelled: float = 0.0, preferred_time_gap: float = 2.0,
                 length: float = 4.4, width: float = 1.82,
                 min_creep_distance: float = 0, maximum_lateral_acceleration: float = 1.1
                 ) -> None:
        """

        :param uid: unique identifier for vehicle
        :param start_time: Simulation time when vehicle is spawned
        :param route: route instance that vehicle is on
        :param speed: initial speed the vehicle [m/s]
        :param acceleration: initial acceleration of the vehicle [m/s**2]
        :param direction: initial direction of the vehicle [radians]
        :param sensing_radius: distance vehicle can detect other vehicles [m]
        :param maximum_acceleration: maximum acceleration of the vehicle [m/s**2]
        :param maximum_deceleration: maximum deceleration of the vehicle [m/s**2]
        :param maximum_speed: maximum speed of the vehicle [m/s**2]
        :param minimum_speed: minimum speed the vehicle [m/s**2]
        :param distance_travelled: distance travelled along a Path [m]
        :param preferred_time_gap: time gap between vehicles [s]
        :param vehicle_length: length of the vehicle [m]
        :param vehicle_width: width of the vehicle [m]
        """
        self.uid = uid
        self.route_uid = route_uid
        self.start_time = start_time
        self.position_data = []
        self._speed = speed
        self._acceleration = acceleration
        self._direction = direction
        self._sensing_radius = sensing_radius
        self._maximum_acceleration = maximum_acceleration
        self._maximum_deceleration = maximum_deceleration
        self._maximum_lateral_acceleration = maximum_lateral_acceleration
        self._maximum_speed = maximum_speed
        self._minimum_speed = minimum_speed
        self._path_distance_travelled = 0.0
        self._preferred_time_gap = preferred_time_gap
        self.length = length
        self.width = width
        self._path_index = 0
        self.changing_lane = False
        self._min_creep_distance = min_creep_distance
        self.wait_time = 0

    def update(self, time_delta: float, object_ahead: "Vehicle", delta_distance_ahead: float, curvature: float = 0.0) -> None:
        """
        :param object_ahead:
        :param delta_distance_ahead:
        :param time_delta: change in time between updates [s]
        """

        if object_ahead is None:
            speed_object_ahead = 100.0
            delta_distance_ahead = 100.0
        else:
            speed_object_ahead = object_ahead.get_speed()
            delta_distance_ahead = delta_distance_ahead - \
                0.5 * (self.length + object_ahead.get_length())

        self._acceleration = self._calculate_acceleration(speed_object_ahead, delta_distance_ahead)

        maximum_speed = min(self._calculate_maximum_speed_due_lateral_acceleration(curvature), self._maximum_speed)
        self._speed = clamp((self._speed + (self._acceleration * time_delta)), self._minimum_speed, maximum_speed)

        self._path_distance_travelled += self._speed * time_delta

    def _calculate_maximum_speed_due_lateral_acceleration(self, curvature):
        return sqrt(self._maximum_lateral_acceleration / (curvature + 1e-6))

    def get_path_index(self):
        return self._path_index

    def update_position_data(self, position_data):
        self.position_data.append(position_data)

    def _calculate_acceleration(self, speed_vehicle_ahead, delta_distance_ahead) -> float:
        """

        :rtype: float
        :param vehicle_ahead: object of the vehicle ahead
        :return: tangential acceleration of the vehicle
        """

        if self._acceleration < 0:
            anticipation_time = 0.4
        else:
            anticipation_time = 1.0

        acceleration = (speed_vehicle_ahead ** 2 - self._speed ** 2 + 2 * self._maximum_deceleration * (
            anticipation_time * (
                speed_vehicle_ahead - self._speed) + delta_distance_ahead - self._speed * self._preferred_time_gap)) / (
            anticipation_time * (
                2 * self._maximum_deceleration * self._preferred_time_gap + self._maximum_deceleration * anticipation_time + 2 * self._speed))

        return clamp(acceleration, -self._maximum_deceleration, self._maximum_acceleration)

    def _nearby_vehicles(self, vehicles):
        """

        :rtype: list
        :param vehicles: list of vehicles within sim
        :return: list of vehicles within detection radius
        """
        nearby_vehicles = []
        for vehicle in vehicles:
            distance = sqrt(sum(pow(x, 2) for x in vehicle.position_data[-1]))
            if distance < self._sensing_radius:
                nearby_vehicles.append(vehicle)

    def get_path_distance_travelled(self) -> float:
        return self._path_distance_travelled

    def increment_path(self, path_distance_travelled: float):
        self._path_distance_travelled = path_distance_travelled
        self._path_index += 1

    def get_speed(self) -> float:
        """

        :rtype: float
        :return: speed of vehicle [m/s]
        """
        return self._speed

    def get_length(self) -> float:
        return self.length + self._min_creep_distance

    def get_acceleration(self) -> float:
        """

        :rtype: float
        :return: acceleration of vehicle [m/s**2]
        """
        return self._acceleration

    def get_preferred_time_gap(self) -> float:
        """

        :rtype: float
        :return: time gap between vehicles [s]
        """
        return self._preferred_time_gap

    def set_speed(self, speed: float) -> None:
        self._speed = speed

    def set_acceleration(self, acceleration: float) -> None:
        self._acceleration = clamp(
            acceleration, -self._maximum_deceleration, self._maximum_acceleration)

    def get_route_uid(self):
        return self.route_uid

    def add_wait_time(self, time):
        self.wait_time += time


class GhostVehicle:
    def __init__(self, uid, path_uid, time_created):
        self.uid = uid
        self.path_uid = path_uid
        self.time_created = time_created
        self.change_time = 1000


class VehicleResults:
    def __init__(self, uid: int, start_time: float, position_data: list) -> None:
        self.uid = uid
        self.start_time = start_time
        self.position_data = position_data

    def total_time(self, time_step_size):
        return self.start_time + len(self.position_data) * time_step_size

    def total_tick(self, time_step_size):
        return (self.start_time / time_step_size) + len(self.position_data)

    def start_tick(self, time_step_size):
        return self.start_time / time_step_size
