from datetime import datetime, timedelta, time
from math import floor
from random import randint, normalvariate as normal
from Library.maths import clamp


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


class Spawning:
    def __init__(self, node_uid, start_time_of_day):
        # https://math.mit.edu/research/highschool/primes/materials/2015/Yi.pdf

        self.node_uid = node_uid

        self.time_of_last_spawn = start_time_of_day
        self.next_spawn_time_delta = 0

        self.time_between_spawns_mean = 0
        self.time_between_spawns_sdev = 0
        self.time_between_spawns_min = 1

        self.time_between_spawns_mean_over_time = [
            60,  # 00:00
            60,  # 01:00
            60,  # 02:00
            80,  # 03:00
            60,  # 04:00
            40,  # 05:00
            20,  # 06:00
            10,  # 07:00
            8,  # 08:00
            10,  # 09:00
            12,  # 10:00
            14,  # 11:00
            15,  # 12:00
            11,  # 13:00
            10,  # 14:00
            10,  # 15:00
            8,  # 16:00
            7,  # 17:00
            6,  # 18:00
            9,  # 19:00
            10,  # 20:00
            20,  # 21:00
            30,  # 22:00
            40,  # 23:00
        ]

        self.time_between_spawns_sdev_over_time = [
            120,  # 00:00
            120,  # 01:00
            120,  # 02:00
            160,  # 03:00
            120,  # 04:00
            80,  # 05:00
            40,  # 06:00
            20,  # 07:00
            8,  # 08:00
            4,  # 09:00
            6,  # 10:00
            7,  # 11:00
            10,  # 12:00
            10,  # 13:00
            20,  # 14:00
            20,  # 15:00
            10,  # 16:00
            6,  # 17:00
            6,  # 18:00
            10,  # 19:00
            20,  # 20:00
            40,  # 21:00
            60,  # 22:00
            80,  # 23:00
        ]

        self.vehicle_length_mean_small = 3.5
        self.vehicle_width_mean_small = 1.7
        self.vehicle_length_sdev_small = 0.75
        self.vehicle_width_sdev_small = 0.2

        self.vehicle_length_mean_big = 7
        self.vehicle_width_mean_big = 2
        self.vehicle_length_sdev_big = 2
        self.vehicle_width_sdev_big = 0.2

        self.vehicle_length_max = 10
        self.vehicle_length_min = 2
        self.vehicle_width_max = 2.2
        self.vehicle_width_min = 1.5

        self.calculate_spawn_probabilities(start_time_of_day)
        self.calculate_next_spawn_time()

    def nudge(self, time: Time):
        time_delta = time - self.time_of_last_spawn
        if time_delta.total_seconds() > self.next_spawn_time_delta:
            self.calculate_spawn_probabilities(time)
            self.time_of_last_spawn = time
            self.calculate_next_spawn_time()
            return True
        return False

    def get_random_vehicle_size(self):
        w = randint(0, 1)
        length = w * normal(self.vehicle_length_mean_small, self.vehicle_length_sdev_small) + (1 - w) * normal(self.vehicle_length_mean_big, self.vehicle_length_sdev_big)
        width = w * normal(self.vehicle_width_mean_small, self.vehicle_width_sdev_small) + (1 - w) * normal(self.vehicle_width_mean_big, self.vehicle_width_sdev_big)
        length = clamp(length, self.vehicle_length_min, self.vehicle_length_max)
        width = clamp(width, self.vehicle_width_min, self.vehicle_width_max)
        return length, width

    def calculate_next_spawn_time(self):
        self.next_spawn_time_delta = normal(self.time_between_spawns_mean, self.time_between_spawns_sdev)
        if self.next_spawn_time_delta < self.time_between_spawns_min:
            self.next_spawn_time_delta = self.time_between_spawns_min

    def calculate_spawn_probabilities(self, time: Time):
        last_hour = time.hour
        next_hour = last_hour + 1
        if next_hour >= 24:
            next_hour = 0

        last_mean = self.time_between_spawns_mean_over_time[last_hour]
        next_mean = self.time_between_spawns_mean_over_time[next_hour]
        self.time_between_spawns_mean = (last_mean * (60 - time.minute) + next_mean * time.minute) / 60

        last_sdev = self.time_between_spawns_sdev_over_time[last_hour]
        next_sdev = self.time_between_spawns_sdev_over_time[next_hour]
        self.time_between_spawns_sdev = (last_sdev * (60 - time.minute) + next_sdev * time.minute) / 60

    def select_route(self, routes):
        index = randint(0, len(routes) - 1)
        return routes[index]
