from Library.infrastructure import Path


class Car:
    def __init__(self, path: Path, velocity: float = 0.0, acceleration: float = 0.0, maximum_acceleration: float = 9.81,
                 maximum_deceleration: float = 6.0, distance_traveled: float = 0.0, preferred_time_gap: float = 2.0,
                 vehicle_length: float = 4.5, maximum_velocity: float = 20.0) -> None:
        """

        :param velocity: initial velocity of the vehicle [m/s]
        :param acceleration: initial acceleration of the vehicle [m/s**2]
        :param maximum_acceleration: maximum acceleration of the vehicle [m/s**2]
        :param distance_traveled: distance traveled along a Path [m]
        """

        self._path = path
        self._velocity = velocity
        self._acceleration = acceleration
        self._vehicle_length = vehicle_length
        self._maximum_acceleration = maximum_acceleration
        self._maximum_deceleration = maximum_deceleration
        self._distance_traveled = distance_traveled
        self._preferred_time_gap = preferred_time_gap
        self._maximum_velocity = maximum_velocity

    def update(self, time_delta: float = 0.033) -> None:
        """

        :param vehicle_ahead: Object of the vehicle ahead
        :rtype: None
        :param time_delta: time step size [s]
        """

        vehicle_ahead = self._path.get_vehicle_ahead(self._distance_traveled)
        self._acceleration = self._calculate_acceleration(vehicle_ahead)
        self._velocity += self._acceleration * time_delta
        self._velocity = min(self._velocity, self._maximum_velocity)
        self._distance_traveled += max(0.0, self._velocity) * time_delta

    def _calculate_acceleration(self, vehicle_ahead: "Car") -> float:
        """

        :rtype: float
        :param vehicle_ahead: Object of the vehicle ahead
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
            delta_distance_ahead = vehicle_ahead.get_distance_traveled() - self._distance_traveled

        acceleration = (velocity_vehicle_ahead ** 2 - self._velocity ** 2 + 2 * self._maximum_deceleration * (anticipation_time * (
                velocity_vehicle_ahead - self._velocity) + delta_distance_ahead - self._velocity * self._preferred_time_gap)) / (
                anticipation_time * (2 * self._maximum_deceleration * self._preferred_time_gap + self._maximum_deceleration * anticipation_time + 2 * self._velocity))

        return min(acceleration, self._maximum_acceleration)

    def get_cartesian_position(self):
        return self._path.get_coordinates(self._distance_traveled)

    def get_distance_traveled(self) -> float:
        return self._distance_traveled

    def get_velocity(self) -> float:
        return self._velocity

    def get_acceleration(self) -> float:
        return self._acceleration

    def get_preferred_time_gap(self) -> float:
        return self._preferred_time_gap

    def get_length(self) -> float:
        return self._vehicle_length

    def set_distance_traveled(self, distance_traveled: float) -> None:
        self._distance_traveled = distance_traveled

    def set_velocity(self, velocity: float) -> None:
        self._velocity = velocity

    def set_acceleration(self, acceleration: float) -> None:
        self._acceleration = min(self._maximum_acceleration, acceleration)
