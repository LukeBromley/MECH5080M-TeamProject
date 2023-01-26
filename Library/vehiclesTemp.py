from Library.infrastructure import Path
import uuid
import math

# CONSTANTS TO BE MOVED
MAXIMUM_VELOCITY = 50.0
MINIMUM_VELOCITY = -50.0
MAXIMUM_ACCELERATION = 10.0
MAXIMUM_DECELERATION = -10.0
CAR_SENSING_RADIUS = 30
# Decisions/Issues
# - Should both Path and Car have describe which path vehicle is on?
# - One array for vehicles, detect distance to all vehicles, path is stored in car?
# - I think car should be x y position, and distance travelled be calculated in path?
# - Matplot lib? Makes car detection easy? Store car as MatLib polygon?
# - Length is only variable
# - UUID.4 for uids?

class Car:
    def __init__(self, path: Path, position_x: float = 0.0, position_y: float = 0.0, velocity: float = 0.0, acceleration: float = 0.0, direction: float = 0.0, 
                 distance_travelled: float = 0.0, vehicle_length: float = 3.5, vehicle_width: float = 2.0, preferred_time_gap: float = 2.0) -> None:
        """

        :param velocity: initial velocity of the vehicle [m/s]
        :param acceleration: initial acceleration of the vehicle [m/s**2]
        :param maximum_acceleration: maximum acceleration of the vehicle [m/s**2]
        :param distance_traveled: distance traveled along a Path [m]
        """
        self._path = path
        self._uid = uuid.uuid4()
        self._position_x = position_x
        self._position_y = position_y
        self._direction = direction
        self._distance_travelled = distance_travelled
        self._velocity = velocity
        self._acceleration = acceleration
        self._length = vehicle_length
        self._width = vehicle_width
        self._preferred_time_gap = preferred_time_gap
        
    def update(self, time_delta: float = 0.1, vehicles: list = []) -> None:
        """
        :param vehicle_ahead: Object of the vehicle ahead
        :rtype: None
        :param time_delta: time step size [s]
        """
        vehicle_ahead = self._vehicle_ahead(self._distance_travelled, vehicles)
        self._acceleration = self._calculate_acceleration(vehicle_ahead)
        self._velocity = self._clamp((self.set_velocity + (self._acceleration * time_delta)), MINIMUM_VELOCITY, MAXIMUM_VELOCITY)
        self._distance_travelled += self._velocity * time_delta

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
            delta_distance_ahead = vehicle_ahead.get_distance_travelled() - self._distance_travelled

        acceleration = (velocity_vehicle_ahead ** 2 - self._velocity ** 2 + 2 * MAXIMUM_DECELERATION * (anticipation_time * (
                velocity_vehicle_ahead - self._velocity) + delta_distance_ahead - self._velocity * self._preferred_time_gap)) / (
                anticipation_time * (2 * MAXIMUM_DECELERATION * self._preferred_time_gap + MAXIMUM_DECELERATION * anticipation_time + 2 * self._velocity))

        return max(min(acceleration, MAXIMUM_ACCELERATION), MAXIMUM_DECELERATION)

    def _vehicle_ahead(self, vehicles):
        vehicles_on_path = [car for car in vehicles if car.get_path == self._path ]
        vehicles_ahead = [car for car in vehicles_on_path if car.get_distance_travelled > self.get_distance_travelled]
        if len(vehicles_ahead) > 0:
            vehicle_ahead = vehicles_ahead[0]
            for car in vehicles_ahead:
                if (car.get_distance_travelled - self.get_distance_travelled) < vehicle_ahead.get_distance_travelled:
                    vehicle_ahead =car
            return vehicle_ahead
        else:
            return None

    def _nearby_vehicles(self, vehicles):
        nearby_vehicles = []
        for car in vehicles:
            distance = math.sqrt(sum(pow(x, 2) for x in car.get_position()))
            if distance < CAR_SENSING_RADIUS:
                nearby_vehicles.append(car)

    def _clamp(n, min, max):
        return max(min(max, n), min)

    def get_position(self) -> list:
        return [self._position_x, self._position_y]

    def get_path(self) -> Path:
        return self._path
    
    def get_distance_travelled(self) -> float:
        return self._distance_travelled()

    def get_velocity(self) -> float:
        return self._velocity

    def get_acceleration(self) -> float:
        return self._acceleration

    def get_preferred_time_gap(self) -> float:
        return self._preferred_time_gap

    def get_dimensions(self) -> float:
        return [self._length, self._width]

    def set_velocity(self, velocity: float) -> None:
        self._velocity = velocity

    def set_acceleration(self, acceleration: float) -> None:
        self._acceleration = min(self._maximum_acceleration, acceleration)

