from Library.infrastructure import Route, TrafficLight
from Library.maths import clamp
from math import sqrt
from typing import List


class Vehicle:
    def __init__(self, route_uid: int, start_time: float = 0.0, uid: int = 0,
                 velocity: float = 0.0, acceleration: float = 0.0,
                 direction: float = 0.0, sensing_radius: float = 0.0,
                 maximum_acceleration: float = 9.81, maximum_deceleration: float = 6.0,
                 maximum_velocity: float = 20.0, minimum_velocity: float = -20.0,
                 distance_travelled: float = 0.0, preferred_time_gap: float = 2.0,
                 length: float = 4.4, width: float = 1.82) -> None:
        """

        :param uid: unique identifier for vehicle
        :param start_time: Simulation time when vehicle is spawned
        :param route: route instance that vehicle is on
        :param velocity: initial velocity of the vehicle [m/s]
        :param acceleration: initial acceleration of the vehicle [m/s**2]
        :param direction: initial direction of the vehicle [radians]
        :param sensing_radius: distance vehicle can detect other vehicles [m]
        :param maximum_acceleration: maximum acceleration of the vehicle [m/s**2]
        :param maximum_deceleration: maximum deceleration of the vehicle [m/s**2]
        :param maximum_velocity: maximum velocity of the vehicle [m/s**2]
        :param minimum_velocity: minimum velocity of the vehicle [m/s**2]
        :param distance_travelled: distance travelled along a Path [m]
        :param preferred_time_gap: time gap between vehicles [s]
        :param vehicle_length: length of the vehicle [m]
        :param vehicle_width: width of the vehicle [m]
        """

        self.uid = uid
        self.route_uid = route_uid
        self.start_time = start_time
        self.position_data = []
        self._velocity = velocity
        self._acceleration = acceleration
        self._direction = direction
        self._sensing_radius = sensing_radius
        self._maximum_acceleration = maximum_acceleration
        self._maximum_deceleration = maximum_deceleration
        self._maximum_velocity = maximum_velocity
        self._minimum_velocity = minimum_velocity
        self._distance_travelled = distance_travelled
        self._preferred_time_gap = preferred_time_gap
        self.length = length
        self.width = width

    def update(self, time_delta: float, object_ahead: "Vehicle", delta_distance_ahead: float) -> None:
        """
        :param object_ahead:
        :param delta_distance_ahead:
        :param time_delta: change in time between updates [s]
        """

        if object_ahead is None:
            velocity_object_ahead = 100.0
            delta_distance_ahead = 100.0
        else:
            velocity_object_ahead = object_ahead.get_velocity()
            delta_distance_ahead = delta_distance_ahead - 0.5*(self.length + object_ahead.get_length())

        self._acceleration = self._calculate_acceleration(velocity_object_ahead, delta_distance_ahead)
        self._velocity = clamp((self._velocity + (self._acceleration * time_delta)), self._minimum_velocity,
                               self._maximum_velocity)
        self._distance_travelled += self._velocity * time_delta

    def update_position_data(self, position_data):
        self.position_data.append(position_data)

    def _calculate_acceleration(self, velocity_vehicle_ahead, delta_distance_ahead) -> float:
        """

        :rtype: float
        :param vehicle_ahead: object of the vehicle ahead
        :return: tangential acceleration of the vehicle
        """

        if self._acceleration < 0:
            anticipation_time = 0.4
        else:
            anticipation_time = 1.0

        acceleration = (velocity_vehicle_ahead ** 2 - self._velocity ** 2 + 2 * self._maximum_deceleration * (
                anticipation_time * (
                velocity_vehicle_ahead - self._velocity) + delta_distance_ahead - self._velocity * self._preferred_time_gap)) / (
                               anticipation_time * (
                               2 * self._maximum_deceleration * self._preferred_time_gap + self._maximum_deceleration * anticipation_time + 2 * self._velocity))

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

    def get_route_distance_travelled(self) -> float:
        """

        :rtype: float
        :return: distanced travelled along path [m]
        """
        return self._distance_travelled

    def get_velocity(self) -> float:
        """

        :rtype: float
        :return: velocity of vehicle [m/s]
        """
        return self._velocity

    def get_length(self) -> float:
        return self.length

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

    def set_distance_travelled(self, distance_travelled: float) -> None:
        self._distance_travelled = distance_travelled

    def set_velocity(self, velocity: float) -> None:
        self._velocity = velocity

    def set_acceleration(self, acceleration: float) -> None:
        self._acceleration = clamp(acceleration, -self._maximum_deceleration, self._maximum_acceleration)


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
