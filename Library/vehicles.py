from lib.infrastructure import Path


class Car:
    def __init__(self, path: Path, velocity: float = 0.0, acceleration: float = 0.0, maximum_acceleration: float = 9.81,
                 distance_traveled: float = 0.0, preferred_time_gap: float = 2.0, vehicle_length: float = 4.5) -> None:
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
        self._distance_traveled = distance_traveled
        self._preferred_time_gap = preferred_time_gap

    def update(self, time_delta: float = 0.033) -> None:
        """

        :rtype: None
        :param time_delta: time step size [s]
        """
        self._velocity += self._acceleration * time_delta
        self._distance_traveled += max(0.0, self._velocity) * time_delta

    def get_x(self):
        return self._path.get_x(self._distance_traveled)


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
