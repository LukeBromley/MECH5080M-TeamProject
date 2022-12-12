import matplotlib.pyplot as plt


class Vehicle:
    def __init__(self, driver: str = None, velocity: float = 0.0, acceleration: float = 0.0,
                 maximum_acceleration: float = 9.81, distance_traveled_longitudinal: float = 0.0,
                 distance_traveled_lateral: float = 0.0, preferred_time_gap: float = 2.0,
                 ax: plt.axis = None, vehicle_length: float = 4.5) -> None:
        """

        :rtype: None
        :param velocity: initial tangential velocity of the vehicle [m/s]
        :param acceleration: initial tangential acceleration of the vehicle [m/s**2]
        :param distance_traveled: distance traveled by the vehicle [m]
        """
        self.driver = driver
        self.velocity = velocity
        self.acceleration = acceleration
        self.vehicle_length = vehicle_length
        self.maximum_acceleration = maximum_acceleration
        self.distance_traveled_longitudinal = distance_traveled_longitudinal
        self.distance_traveled_lateral = distance_traveled_lateral
        self.preferred_time_gap = preferred_time_gap

    def update(self, time_delta: float = 0.033) -> None:
        """

        :rtype: None
        :param time_delta: iteration length [s]
        """
        self.velocity += self.acceleration * time_delta
        self.distance_traveled_longitudinal += max(0.0, self.velocity) * time_delta

    def get_distance_traveled_longitudinal(self) -> float:
        return self.distance_traveled_longitudinal

    def get_distance_traveled_lateral(self) -> float:
        return self.distance_traveled_lateral

    def get_velocity(self) -> float:
        return self.velocity

    def get_acceleration(self) -> float:
        return self.acceleration

    def get_preferred_time_gap(self) -> float:
        return self.preferred_time_gap

    def get_length(self) -> float:
        return self.vehicle_length

    def set_distance_traveled(self, distance_traveled: float) -> None:
        self.distance_traveled_longitudinal = distance_traveled

    def set_velocity(self, velocity: float) -> None:
        self.velocity = velocity

    def set_acceleration(self, acceleration: float) -> None:
        self.acceleration = min(self.maximum_acceleration, acceleration)
