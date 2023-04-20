from datetime import datetime, timedelta, time
from math import floor, log, gamma, pow, exp
from random import random, randint, uniform, normalvariate as normal, choices
from library.maths import clamp


class SimulationConfiguration:
    def __init__(self):
        """

        Struct like class that contains parameters to configure simulation parameters

        """

        # Time
        self.tick_rate = 100
        self.start_time_of_day = Time(12, 0, 0)  # ticks per second
        self.simulation_duration = 8640000

        # Vehicle
        self.initial_speed = 5.0
        self.initial_acceleration = 0.0
        self.maximum_acceleration = 3.0
        self.maximum_deceleration = 9.0
        self.maximum_lateral_acceleration = 2.0
        self.autonomous_preferred_time_gap = 1.0
        self.human_preferred_time_gap = 2.0
        self.preferred_time_gap = 2.0
        self.maximum_speed = 30.0
        self.minimum_speed = 0.0
        self.min_creep_distance = 1

        # Spawning
        self.random_seed = 1
        self.max_spawn_time = 30
        self.min_spawn_time = 2
        self.mean_spawn_time_per_hour = [5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5]
        self.sdev_spawn_time_per_hour = [3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3]
        self.min_spawn_time_per_hour = [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2]
        self.distribution_method = 'gamma'

        self.max_vehicle_length = 3.5
        self.min_vehicle_length = 2.5
        self.max_vehicle_width = 2
        self.min_vehicle_width = 1.6

        self.mean_vehicle_lengths = [3]
        self.mean_vehicle_widths = [1.8]
        self.sdev_vehicle_lengths = [0.1]
        self.sdev_vehicle_widths = [0.1]

        self.mass_per_cross_sectional_area = 0

        self.autonomous_driver_probability = 1

        # Visualiser
        self.visualiser_scale = 100


class MachineLearningConfiguration:
    def __init__(self):
        """

        Struct like class that contains parameters to configure machine learning parameters

        """

        # Config
        self.config_id = 0
        # Limits
        self.max_steps_per_episode = 0
        self.episode_end_reward = 0
        self.solved_mean_reward = 0
        self.reward_history_limit = 0
        # Action Probabilities
        self.random_action_selection_probabilities = [1]
        self.epsilon_greedy_min = 0.0
        self.epsilon_greedy_max = 0.0
        # Exploration
        self.number_of_steps_of_required_exploration = 0
        self.number_of_steps_of_exploration_reduction = 0
        # Update
        self.update_after_actions = 0
        self.update_target_network = 0
        # Look Into Future
        self.seconds_to_look_into_the_future = 0.0
        # Sample Size
        self.sample_size = 0
        # Discount factor
        self.gamma = 0.0
        # Maximum replay buffer length
        self.max_replay_buffer_length = 0.0
        # Optimisations
        self.learning_rate = 0.0
        self.ml_model_hidden_layers = [1]


class Time:
    def __init__(self, hour, minute, second, millisecond=0):
        """

        Class that is used to store simulation time. Built on the functionality of datetime. Has additional
        functionality for our simulation and simplifies use.

        :param hour: Hours
        :param minute: Minutes
        :param second: Seconds
        :param millisecond: Milliseconds
        """
        self.hour = hour
        self.minute = minute
        self.second = second
        self.millisecond = millisecond

    def add_hours(self, hours: int) -> object:
        """
        The add_hours function adds the number of hours specified by the user to the self time object.
        It returns a new Time object with the updated time.

        :param hours: Number of hours to add to the time object
        :return: The new time object with the added hours
        """
        new_time = datetime(1, 1, 1, self.hour, self.minute, self.second) + timedelta(hours=hours)
        return Time(new_time.hour, new_time.minute, new_time.second, self.millisecond)

    def add_minutes(self, minutes: int) -> object:
        """
        The add_minutes function adds the number of minutes specified by the user to the self time object.
        It returns a new Time object with the updated time.

        :param minutes: Number of minutes to add to the time object
        :return: The new time object with the added minutes
        """
        new_time = datetime(1, 1, 1, self.hour, self.minute, self.second) + timedelta(minutes=minutes)
        return Time(new_time.hour, new_time.minute, new_time.second, self.millisecond)

    def add_seconds(self, seconds: int) -> object:
        """
        The add_seconds function adds the number of seconds specified by the user to the self time object.
        It returns a new Time object with the updated time.

        :param seconds: Number of seconds to add to the time object
        :return: The new time object with the added seconds
        """
        new_time = datetime(1, 1, 1, self.hour, self.minute, self.second) + timedelta(seconds=seconds)
        return Time(new_time.hour, new_time.minute, new_time.second, self.millisecond)

    def add_milliseconds(self, milliseconds: int) -> object:
        """
        The add_milliseconds function adds the number of milliseconds specified by the user to the self time object.
        It returns a new Time object with the updated time.

        :param milliseconds: Number of milliseconds to add to the time object
        :return: The new time object with the added milliseconds
        """
        new_time = datetime(1, 1, 1, self.hour, self.minute, self.second, microsecond=self.millisecond * 1000) + timedelta(milliseconds=milliseconds)
        return Time(new_time.hour, new_time.minute, new_time.second, floor(new_time.microsecond / 1000))

    def total_seconds(self) -> int:
        """
        The total_seconds function returns the total number of seconds in the Time object.

        :return: The total number of seconds
        """
        return 60 * 60 * self.hour + 60 * self.minute + self.second

    def total_milliseconds(self) -> int:
        """
        The total_milliseconds function returns the total number of milliseconds in the Time object.

        :return: The total number of milliseconds
        """
        return self.total_seconds() * 1000 + self.millisecond

    def __str__(self) -> str:
        """
        The __str__ function returns a string representation of the time object in the format HH:MM:SS:mm.
        This is what you see when you print an object, or convert it to a string using str().

        :return: Time as a string
        """
        return str(self.hour).zfill(2) + ":" + str(self.minute).zfill(2) + ":" + str(self.second).zfill(2) + ":" + str(self.millisecond).zfill(3)

    def __add__(self, other) -> object:
        """
        The __add__ function adds another Time objects together.

        :param other: Other time object to add to the current time object
        :return: A new time object that is the sum of the two times
        """
        new_time = datetime(1, 1, 1, self.hour, self.minute, self.second) + timedelta(hours=other.hour, minutes=other.minute, seconds=other.second)
        return Time(new_time.hour, new_time.minute, new_time.second, self.millisecond)

    def __sub__(self, other) -> object:
        """
        The __sub__ function subtracts another Time object from the self time object.

        :param other: Time object to subtract
        :return: A new time object that represents the difference between two times
        """
        new_time = datetime(1, 1, 1, self.hour, self.minute, self.second) - timedelta(hours=other.hour, minutes=other.minute, seconds=other.second)
        return Time(new_time.hour, new_time.minute, new_time.second, self.millisecond)


class SpawningStats:
    def __init__(self,
                 max_spawn_time: float = 300,
                 min_spawn_time: float = 2,
                 mean_spawn_time_per_hour: float = 5,
                 sdev_spawn_time_per_hour: float = 3,
                 min_spawn_time_per_hour: float = 2,
                 distribution_method: str = 'gamma',

                 max_vehicle_length: float = 10,
                 min_vehicle_length: float = 2,
                 max_vehicle_width: float = 2.5,
                 min_vehicle_width: float = 1.5,

                 mean_vehicle_lengths: list = (3, 5, 8),
                 mean_vehicle_widths: list = (1.8, 2, 2.2),
                 sdev_vehicle_lengths: list = (0.5, 1, 2),
                 sdev_vehicle_widths: list = (0.2, 0.2, 0.2),
                 mass_per_cross_sectional_area: float = 0,
                 autonomous_driver_probability: float = 1
                 ):

        """
        Struct like class that contains parameters to configure spawning distributions

        :param max_spawn_time: Limits the spawn time delta to below this value
        :param min_spawn_time: Limits the spawn time delta to above this value
        :param mean_spawn_time_per_hour: List of mean spawn time deltas for each hour of the day.
        :param sdev_spawn_time_per_hour: List of standard deviation of spawn time deltas for each hour of the day.
        :param min_spawn_time_per_hour: List of minimum spawn time offset for each hour of the day. Used for weibull
        distributions only.
        :param distribution_method: Random distribution method to be used for calculating randomised spawn time deltas
        :param max_vehicle_length: Limits the vehicle length to below this value
        :param min_vehicle_length: Limits the vehicle length to above this value
        :param max_vehicle_width: Limits the vehicle width to below this value
        :param min_vehicle_width: Limits the vehicle width to above this value
        :param mean_vehicle_lengths: List of mean vehicle lengths for multi-modal normal distribution
        :param mean_vehicle_widths: List of mean vehicle widths for multi-modal normal distribution
        :param sdev_vehicle_lengths: List of vehicle length standard deviations for multi-modal normal distribution
        :param sdev_vehicle_widths: List of vehicle width standard deviations for multi-modal normal distribution
        :param mass_per_cross_sectional_area: Mass per cross sectional area
        :param autonomous_driver_probability: Probability of a spawned vehicle being autonomous. Range 0-1
        """

        # SPAWNING TIMING
        # Max/Min
        self.max_spawn_time = max_spawn_time
        self.min_spawn_time = min_spawn_time
        # Statistics
        self.mean_spawn_time_per_hour = mean_spawn_time_per_hour
        self.sdev_spawn_time_per_hour = sdev_spawn_time_per_hour
        self.min_spawn_time_per_hour = min_spawn_time_per_hour
        # Distribution method
        self.distribution_method = distribution_method

        # VEHICLE SIZE
        # Max/Min
        self.max_vehicle_length = max_vehicle_length
        self.min_vehicle_length = min_vehicle_length
        self.max_vehicle_width = max_vehicle_width
        self.min_vehicle_width = min_vehicle_width
        # Statistics
        self.mean_vehicle_lengths = mean_vehicle_lengths
        self.mean_vehicle_widths = mean_vehicle_widths
        self.sdev_vehicle_lengths = sdev_vehicle_lengths
        self.sdev_vehicle_widths = sdev_vehicle_widths
        # Weight
        self.mass_per_cross_sectional_area = mass_per_cross_sectional_area

        # DRIVER TYPES
        self.autonomous_driver_probability = autonomous_driver_probability


class SpawningRandom:
    def __init__(self, node_uid: int, start_time_of_day: Time, spawning_stats: SpawningStats):
        """

        Spawns vehicles at randomly distributed time deltas. SpawningStats class provided configures the spawning
        behavior (obtained from simulation config). The random method currently has normally distributed spawning and weibull spawning implemented.
        Weibull is a better distribution and is more accurate.

        :param node_uid: Node that vehicles will be spawned at
        :param start_time_of_day: Simulation time of day at simulation start
        :param spawning_stats: Parameters to configure spawning behvaior
        """

        # Running variables
        self.node_uid = node_uid
        self.time_of_last_spawn = start_time_of_day
        self.next_spawn_time_delta = 0

        # Spawning distribution parameters
        self.spawning_stats = spawning_stats
        self.current_mean_spawn_time = 0
        self.current_sdev_spawn_time = 0
        self.current_min_spawn_time = 0

        # Initial update
        self.calculate_spawn_probabilities(start_time_of_day)
        self.calculate_next_spawn_time(distribution_type=self.spawning_stats.distribution_method)

    def nudge(self, time: Time) -> bool:
        """
        The nudge function is called by the simulation to determine if a new vehicle should be spawned. It returns True
        if a vehicle should be spawn, and False otherwise. Time is required to determine if the spawn time delt has
        elapsed or not.

        :param time: Time: Calculate the time delta between the last spawn and this one
        :return: Boolean
        """
        time_delta = time - self.time_of_last_spawn
        if time_delta.total_seconds() > self.next_spawn_time_delta:
            self.time_of_last_spawn = time
            self.calculate_next_spawn_time(distribution_type=self.spawning_stats.distribution_method)
            return True
        return False

    def get_random_vehicle_size(self) -> tuple:
        """
        The get_random_vehicle_size function returns a tuple of length and width of a vehicle using multimodal
        distributions stored in the simulation configuration. The mean and standard deviation is randomly selected
        and then this is used to calculate a value from a normal distribution.

        :return: A tuple of length and width
        """
        i = randint(0, len(self.spawning_stats.mean_vehicle_lengths) - 1)
        length = self._calculate_multi_modal_distribution(i, self.spawning_stats.mean_vehicle_lengths, self.spawning_stats.sdev_vehicle_lengths)
        width = self._calculate_multi_modal_distribution(i, self.spawning_stats.mean_vehicle_widths, self.spawning_stats.mean_vehicle_widths)
        length = clamp(length, self.spawning_stats.min_vehicle_length, self.spawning_stats.max_vehicle_length)
        width = clamp(width, self.spawning_stats.min_vehicle_width, self.spawning_stats.max_vehicle_width)
        return length, width

    def _calculate_multi_modal_distribution(self, i: int, means: list, sdevs: list) -> float:
        """
        This is a helper function that calculates a value from a multi-modal normal distribution

        :param i: int: mean or index list index
        :param means: list of means
        :param sdevs: list of standard deviations
        :return: value
        """
        assert len(means) == len(sdevs)
        return normal(means[i], sdevs[i])

    def get_vehicle_mass(self, length, width) -> tuple:
        """
        The get_random_vehicle_size function returns a tuple of length and width of a vehicle using multimodal
        distributions stored in the simulation configuration. The mean and standard deviation is randomly selected
        and then this is used to calculate a value from a normal distribution.

        :return: A tuple of length and width
        """
        return length * width * self.spawning_stats.mass_per_cross_sectional_area

    def calculate_next_spawn_time(self, distribution_type: str = 'gamma') -> None:
        """
        The calculate_next_spawn_time function uses the probability distribution methods to calculate the next spawn
        time. The function also constrains the spawn time between limits

        :param distribution_type: str: Select which distribution to use for calculating the next spawn time
        :return: None
        """

        if distribution_type == 'normal':
            self.next_spawn_time_delta = self.normal(self.current_mean_spawn_time, self.current_sdev_spawn_time)
        elif distribution_type == 'weibull':
            self.next_spawn_time_delta = self.weibull(self.current_mean_spawn_time, self.current_sdev_spawn_time, self.current_min_spawn_time)
        else:
            alpha = 1.0354 * self.current_mean_spawn_time - 0.8897
            beta = 1 / alpha
            self.next_spawn_time_delta = self.gamma(alpha, beta)
        if self.next_spawn_time_delta < self.spawning_stats.min_spawn_time:
            self.next_spawn_time_delta = self.spawning_stats.min_spawn_time
        if self.spawning_stats.max_spawn_time is not None:
            if self.next_spawn_time_delta > self.spawning_stats.max_spawn_time:
                self.next_spawn_time_delta = self.spawning_stats.max_spawn_time

    def normal(self, mean: float, sdev: float):
        """
        The normal function is a probability distribution function that we use to determine time delta between vehicle
        spawns. It requires two parameters: mean, sdev. These can be determined from measuring the vehicles approaching a
        real junction. In practice, a more realistic distribution is the weibull function below.

        :param mean: Mean spawn time
        :param sdev: Standard deviation of spawn time
        :return: Random time delta based off the distribution probabilities
        """
        return normal(mean, sdev)

    def weibull(self, mean: float, sdev: float, min_offset: float = 0):
        """
        The weibull function is a probability distribution function that we use to determine time delta between vehicle
        spawns. It requires three parameters: mean, sdev, and min_offset. These can be determined from measuring the
        vehicles approaching a real junction.

        :param mean: Mean spawn time
        :param sdev: Standard deviation of spawn time
        :param min_offset: Shift the distribution to the right (prevent spawn times of less than min_offset).
        :return: Random time delta based off the distribution probabilities
        """
        signal_to_noise_ratio = mean / sdev
        shape = signal_to_noise_ratio**(-1.086)
        scale = mean / gamma(1+(1/shape))
        u = random()
        x = scale * (-log(u)) ** (1 / shape) + min_offset
        return x

    def gamma(self, alpha: float, beta: float):
        """
        The weibull function is a probability distribution function that we use to determine time delta between vehicle
        spawns. It requires three parameters: mean, sdev, and min_offset. These can be determined from measuring the
        vehicles approaching a real junction.

        Source: https://e-maxx.ru/bookz/files/numerical_recipes.pdf

        :param alpha: Mean spawn time
        :param beta: Standard deviation of spawn time
        :return: Random time delta based off the distribution probabilities
        """
        assert alpha > 0 and beta > 0

        # Transform u1 and u2 using the inverse transform method
        x = (-1 / beta) * log(uniform(0, 1))
        y = pow(x, alpha - 1)
        z = y * exp(-x) / gamma(alpha)

        # Reject samples that fall outside the distribution
        while uniform(0, 1) > z:
            u1 = uniform(0, 1)
            x = (-1 / beta) * log(u1)
            y = pow(x, alpha - 1)
            z = y * exp(-x) / gamma(alpha)

        return x

    def calculate_spawn_probabilities(self, time: Time) -> None:
        """
        The calculate_spawn_probabilities function updates the current mean and standard deviation for spawn times,
        based the mean and standard deviation stored in the SpawningStats class. The function takes in a Time object as
        an argument, and uses that to determine what hour it is currently (and thus what mean/standard deviation values
        to use).

        :param time: Time: Calculate the current mean spawn time and standard deviation of spawn time
        :return: None
        """
        last_hour = time.hour
        next_hour = last_hour + 1
        if next_hour >= 24:
            next_hour = 0

        if type(self.spawning_stats.mean_spawn_time_per_hour) == list:
            last_mean = self.spawning_stats.mean_spawn_time_per_hour[last_hour]
            next_mean = self.spawning_stats.mean_spawn_time_per_hour[next_hour]
        else:
            last_mean = self.spawning_stats.mean_spawn_time_per_hour
            next_mean = self.spawning_stats.mean_spawn_time_per_hour
        self.current_mean_spawn_time = (last_mean * (60 - time.minute) + next_mean * time.minute) / 60

        if type(self.spawning_stats.sdev_spawn_time_per_hour) == list:
            last_sdev = self.spawning_stats.sdev_spawn_time_per_hour[last_hour]
            next_sdev = self.spawning_stats.sdev_spawn_time_per_hour[next_hour]
        else:
            last_sdev = self.spawning_stats.sdev_spawn_time_per_hour
            next_sdev = self.spawning_stats.sdev_spawn_time_per_hour
        self.current_sdev_spawn_time = (last_sdev * (60 - time.minute) + next_sdev * time.minute) / 60

        if type(self.spawning_stats.sdev_spawn_time_per_hour) == list:
            last_min_spawn_time = self.spawning_stats.min_spawn_time_per_hour[last_hour]
            next_min_spawn_time = self.spawning_stats.min_spawn_time_per_hour[next_hour]
        else:
            last_min_spawn_time = self.spawning_stats.min_spawn_time_per_hour
            next_min_spawn_time = self.spawning_stats.min_spawn_time_per_hour
        self.current_min_spawn_time = (last_min_spawn_time * (60 - time.minute) + next_min_spawn_time * time.minute) / 60

    def select_route(self, routes):
        """
        The select_route function takes in a list of routes and returns one route at random.

        :param routes: List of routes that the vehicle can take
        :return: A random route from the routes list
        """
        index = randint(0, len(routes) - 1)
        return routes[index]

    def get_vehicle_driver_type(self):
        if choices([0, 1], weights=[self.spawning_stats.autonomous_driver_probability, 1 - self.spawning_stats.autonomous_driver_probability], cum_weights=None, k=1) == 0:
            return "autonomous"
        else:
            return "human"


class SpawningFixed(SpawningRandom):
    def __init__(self, node_uid: int, start_time_of_day: Time, spawning_time: float = 3, vehicle_size: tuple = (3, 1.8)):
        """

        Spawns vehicles at fixed time deltas with a fixed size. Uses SpawningRandom class but provides a spawning stats class
        that produces spawns vehicles at fixed time intervals.
        This is mainly used for debugging.

        :param node_uid: Node that vehicles will be spawned at
        :param start_time_of_day: Simulation time of day at simulation start
        :param spawning_time: Simulation time
        :param vehicle_size: Specifies a fixed vehicle size
        """

        spawning_stats = SpawningStats(
            max_spawn_time=spawning_time,
            min_spawn_time=spawning_time,
            mean_spawn_time_per_hour=spawning_time,
            sdev_spawn_time_per_hour=0,
            min_spawn_time_per_hour=2,
            distribution_method='normal',

            max_vehicle_length=vehicle_size[0],
            min_vehicle_length=vehicle_size[0],
            max_vehicle_width=vehicle_size[1],
            min_vehicle_width=vehicle_size[1],

            mean_vehicle_lengths=[vehicle_size[0]],
            mean_vehicle_widths=[vehicle_size[1]],
            sdev_vehicle_lengths=[0],
            sdev_vehicle_widths=[0]
        )

        super().__init__(node_uid, start_time_of_day, spawning_stats)
