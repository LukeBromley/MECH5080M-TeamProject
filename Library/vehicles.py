from Library.infrastructure import Path
from Library.maths import clamp
from math import sqrt


class Car:
    def __init__(self, path: Path, start_time: float = 0.0, uid: int = 0,
                 velocity: float = 0.0, acceleration: float = 0.0,
                 direction: float = 0.0, sensing_radius: float = 0.0,
                 maximum_acceleration: float = 9.81, maximum_deceleration: float = 6.0,
                 maximum_velocity: float = 20.0, minimum_velocity: float = -20.0,
                 distance_travelled: float = 0.0, preferred_time_gap: float = 2.0,
                 vehicle_length: float = 4.4, vehicle_width: float = 1.82) -> None:
        """

        :param uid: unique identifier for vehicle
        :param start_time: Simulation time when vehicle is spawned
        :param path: path instance that vehicle is on
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
        self._path = path
        self._start_time = start_time
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
        self._vehicle_length = vehicle_length
        self._vehicle_width = vehicle_width

        self.position_data = []

    def update(self, time_delta: float = 0.1, vehicles: list = []) -> None:
        """
        :param time_delta: change in time between updates [s]
        :param vehicles: list of vehicles within sim
        """
        vehicle_ahead = self._vehicle_ahead(vehicles)
        self._acceleration = self._calculate_acceleration(vehicle_ahead)
        self._velocity = clamp(
            (self._velocity + (self._acceleration * time_delta)), self._minimum_velocity, self._maximum_velocity)
        self._distance_travelled += self._velocity * time_delta
        self.position_data.append(self.get_position)

    def _calculate_acceleration(self, vehicle_ahead: "Car") -> float:
        """

        :rtype: float
        :param vehicle_ahead: object of the vehicle ahead
        :return: tangential acceleration of the vehicle
        """

        if self._acceleration < 0:
            anticipation_time = 0.4
        else:
            anticipation_time = 2.0

        if vehicle_ahead is None:
            velocity_vehicle_ahead = 100.0
            delta_distance_ahead = 100.0
        else:
            velocity_vehicle_ahead = vehicle_ahead.get_velocity()
            delta_distance_ahead = vehicle_ahead.get_distance_travelled() - \
                self._distance_travelled

        acceleration = (velocity_vehicle_ahead ** 2 - self._velocity ** 2 + 2 * self._maximum_deceleration * (anticipation_time * (
            velocity_vehicle_ahead - self._velocity) + delta_distance_ahead - self._velocity * self._preferred_time_gap)) / (
            anticipation_time * (2 * self._maximum_deceleration * self._preferred_time_gap + self._maximum_deceleration * anticipation_time + 2 * self._velocity))

        return clamp(acceleration, -(self._maximum_deceleration), self._maximum_acceleration)

    def _vehicle_ahead(self, vehicles):
        """

        :rtype: Car
        :param vehicles: list of vehicles within sim
        :return: object of vehicle ahead
        """
        vehicles_on_path = [
            car for car in vehicles if car.get_path == self._path]
        vehicles_ahead = [
            car for car in vehicles_on_path if car.get_distance_travelled > self.get_distance_travelled]
        if len(vehicles_ahead) > 0:
            vehicle_ahead = vehicles_ahead[0]
            for car in vehicles_ahead:
                if (car.get_distance_travelled - self.get_distance_travelled) < vehicle_ahead.get_distance_travelled:
                    vehicle_ahead = car
            return vehicle_ahead
        else:
            return None

    def _nearby_vehicles(self, vehicles):
        """

        :rtype: list
        :param vehicles: list of vehicles within sim
        :return: list of vehicles within detection radius
        """
        nearby_vehicles = []
        for car in vehicles:
            distance = sqrt((sum(pow(x, 2) for x in car.get_position())), -2)
            if distance < self._sensing_radius:
                nearby_vehicles.append(car)

    def get_position(self):
        """

        :rtype: list
        :return: x and y coordinates
        """
        x, y = self._path.calculate_coords(self._distance_travelled)
        return [x, y]

    def get_path(self) -> Path:
        """

        :rtype: Path
        :return: path that vehicle is on
        """
        return self._path
    
    def get_distance_travelled(self) -> float:
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

    def get_dimensions(self) -> float:
        return [self._vehicle_length, self._vehicle_width]

    def set_distance_travelled(self, distance_travelled: float) -> None:
        self._distance_travelled = distance_travelled

    def set_velocity(self, velocity: float) -> None:
        self._velocity = velocity

    def set_acceleration(self, acceleration: float) -> None:
        self._acceleration = clamp(
            acceleration, -(self._maximum_deceleration), self._maximum_acceleration)
