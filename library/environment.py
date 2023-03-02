from datetime import datetime, timedelta, time
from math import floor
from random import randint, normalvariate as normal
from library.maths import clamp


class SimulationConfiguration:

    def __init__(self):
        # Time
        self.tick_rate = 100
        self.start_time_of_day = Time(12, 0, 0)  # ticks per second
        self.simulation_duration = 8640000

        # Vehicle
        self.initial_speed = 5.0
        self.initial_acceleration = 0.0
        self.maximum_acceleration = 3.0
        self.maximum_deceleration = 9.0
        self.preferred_time_gap = 2.0
        self.maximum_speed = 30.0
        self.min_creep_distance = 1

        # Spawning
        self.random_seed = 1
        self.max_spawn_time = 30
        self.min_spawn_time = 2
        self.mean_spawn_time_per_hour = [5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5]
        self.sdev_spawn_time_per_hour = [3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3]

        self.max_car_length = 3.5
        self.min_car_length = 2.5
        self.max_car_width = 2
        self.min_car_width = 1.6

        self.mean_car_lengths = [3]
        self.mean_car_widths = [1.8]
        self.sdev_car_lengths = [0.1]
        self.sdev_car_widths = [0.1]

        # Visualiser
        self.visualiser_scale = 100

class MachineLearningConfiguration:
    def __init__(self):
        # Config
        self.config_id = 0

        # Limits
        self.max_steps_per_episode = 100000  # Maximum number of steps allowed per episode
        self.episode_end_reward = -500000  # Single episode total reward minimum threshold to end episode
        self.solved_mean_reward = 100000  # Single episode total reward minimum threshold to consider ML trained

        # Action Probabilities
        self.random_action_do_nothing_probability = 0.9  # Probability of the "Do nothing" action
        self.epsilon_greedy_min = 0.1  # Minimum probability of selecting a random action
        self.epsilon_greedy_max = 1.0  # Maximum probability of selecting a random action

        # Exploration
        self.number_of_steps_of_required_exploration = 1000  # 10000  # Number of steps of just random actions before the network can make some decisions
        self.number_of_steps_of_exploration_reduction = 5000  # 50000 # Number of steps over which epsilon greedy decays

        # Sample Size
        self.sample_size = 32  # Size of batch taken from replay buffer

        # Discount factor
        self.gamma = 0.9  # Discount factor for past rewards

        # Maximum replay buffer length
        self.max_replay_buffer_length = 100000

        # Optimisations
        self.learning_rate = 0.01

        # Train the model after number of actions
        self.update_after_actions = 10

        # How often to update the target network
        self.update_target_network = 10000


class Time:
    def __init__(self, hour, minute, second, millisecond=0):
        self.hour = hour
        self.minute = minute
        self.second = second
        self.millisecond = millisecond

    def __str__(self):
        return str(self.hour).zfill(2) + ":" + str(self.minute).zfill(2) + ":" + str(self.second).zfill(2) + ":" + str(self.millisecond).zfill(3)

    def add_hours(self, hours):
        new_time = datetime(1, 1, 1, self.hour, self.minute, self.second) + timedelta(hours=hours)
        return Time(new_time.hour, new_time.minute, new_time.second, self.millisecond)

    def add_minutes(self, minutes):
        new_time = datetime(1, 1, 1, self.hour, self.minute, self.second) + timedelta(minutes=minutes)
        return Time(new_time.hour, new_time.minute, new_time.second, self.millisecond)

    def add_seconds(self, seconds):
        new_time = datetime(1, 1, 1, self.hour, self.minute, self.second) + timedelta(seconds=seconds)
        return Time(new_time.hour, new_time.minute, new_time.second, self.millisecond)

    def add_milliseconds(self, milliseconds):
        new_time = datetime(1, 1, 1, self.hour, self.minute, self.second, microsecond=self.millisecond * 1000) + timedelta(milliseconds=milliseconds)
        return Time(new_time.hour, new_time.minute, new_time.second, floor(new_time.microsecond / 1000))

    def total_seconds(self):
        return 60 * 60 * self.hour + 60 * self.minute + self.second

    def total_milliseconds(self):
        return self.total_seconds() * 1000 + self.millisecond

    def __add__(self, other):
        new_time = datetime(1, 1, 1, self.hour, self.minute, self.second) + timedelta(hours=other.hour, minutes=other.minute, seconds=other.second)
        return Time(new_time.hour, new_time.minute, new_time.second, self.millisecond)

    def __sub__(self, other):
        new_time = datetime(1, 1, 1, self.hour, self.minute, self.second) - timedelta(hours=other.hour, minutes=other.minute, seconds=other.second)
        return Time(new_time.hour, new_time.minute, new_time.second, self.millisecond)


class SpawningStats:
    def __init__(self,
                 max_spawn_time=300,
                 min_spawn_time=2,
                 mean_spawn_time_per_hour=5,
                 sdev_spawn_time_per_hour=3,

                 max_car_length=10,
                 min_car_length=2,
                 max_car_width=2.5,
                 min_car_width=1.5,

                 mean_car_lengths=(3, 5, 8),
                 mean_car_widths=(1.8, 2, 2.2),
                 sdev_car_lengths=(0.5, 1, 2),
                 sdev_car_widths=(0.2, 0.2, 0.2),
                 ):
        # SPAWNING TIMING
        # Max/Min
        self.max_spawn_time = max_spawn_time
        self.min_spawn_time = min_spawn_time
        # Statistics
        self.mean_spawn_time_per_hour = mean_spawn_time_per_hour
        self.sdev_spawn_time_per_hour = sdev_spawn_time_per_hour

        # CAR SIZE
        # Max/Min
        self.max_car_length = max_car_length
        self.min_car_length = min_car_length
        self.max_car_width = max_car_width
        self.min_car_width = min_car_width
        # Statistics
        self.mean_car_lengths = mean_car_lengths
        self.mean_car_widths = mean_car_widths
        self.sdev_car_lengths = sdev_car_lengths
        self.sdev_car_widths = sdev_car_widths


class SpawningRandom:
    def __init__(self, node_uid, start_time_of_day, spawning_stats: SpawningStats):
        # https://math.mit.edu/research/highschool/primes/materials/2015/Yi.pdf

        # Standard Spawning Variables
        self.node_uid = node_uid
        self.time_of_last_spawn = start_time_of_day
        self.next_spawn_time_delta = 0

        # Vehicle Size
        self.spawning_stats = spawning_stats
        self.current_mean_spawn_time = 0
        self.current_sdev_spawn_time = 0

        self.calculate_spawn_probabilities(start_time_of_day)
        self.calculate_next_spawn_time()

    def nudge(self, time: Time):
        time_delta = time - self.time_of_last_spawn
        if time_delta.total_seconds() > self.next_spawn_time_delta:
            self.time_of_last_spawn = time
            self.calculate_next_spawn_time()
            return True
        return False

    def get_random_vehicle_size(self):
        i = randint(0, len(self.spawning_stats.mean_car_lengths) - 1)
        length = self._calculate_multi_modal_distribution(i, self.spawning_stats.mean_car_lengths, self.spawning_stats.sdev_car_lengths)
        width = self._calculate_multi_modal_distribution(i, self.spawning_stats.mean_car_widths, self.spawning_stats.mean_car_widths)
        length = clamp(length, self.spawning_stats.min_car_length, self.spawning_stats.max_car_length)
        width = clamp(width, self.spawning_stats.min_car_width, self.spawning_stats.max_car_width)
        return length, width

    def _calculate_multi_modal_distribution(self, i, means, sdevs):
        assert len(means) == len(sdevs)
        return normal(means[i], sdevs[i])

    def calculate_next_spawn_time(self):
        self.next_spawn_time_delta = normal(self.current_mean_spawn_time, self.current_sdev_spawn_time)
        if self.next_spawn_time_delta < self.spawning_stats.min_spawn_time:
            self.next_spawn_time_delta = self.spawning_stats.min_spawn_time
        if self.spawning_stats.max_spawn_time is not None:
            if self.next_spawn_time_delta > self.spawning_stats.max_spawn_time:
                self.next_spawn_time_delta = self.spawning_stats.max_spawn_time

    def calculate_spawn_probabilities(self, time: Time):
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

    def select_route(self, routes):
        index = randint(0, len(routes) - 1)
        return routes[index]


class SpawningFixed(SpawningRandom):
    def __init__(self, node_uid, start_time_of_day, spawning_time=3, vehicle_size=(3, 1.8)):

        spawning_stats = SpawningStats(
            max_spawn_time=spawning_time,
            min_spawn_time=spawning_time,
            mean_spawn_time_per_hour=spawning_time,
            sdev_spawn_time_per_hour=0,

            max_car_length=vehicle_size[0],
            min_car_length=vehicle_size[0],
            max_car_width=vehicle_size[1],
            min_car_width=vehicle_size[1],

            mean_car_lengths=[vehicle_size[0]],
            mean_car_widths=[vehicle_size[1]],
            sdev_car_lengths=[0],
            sdev_car_widths=[0]
        )

        super().__init__(node_uid, start_time_of_day, spawning_stats)
