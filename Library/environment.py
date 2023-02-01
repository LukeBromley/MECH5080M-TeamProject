from datetime import datetime, timedelta, time
from math import floor


class Time:
    def __init__(self, hour, minute, second, millisecond=0):
        self.hour = hour
        self.minute = minute
        self.second = second
        self.millisecond = millisecond

    def __str__(self):
        return str(self.hour).zfill(2) + ":" + str(self.minute).zfill(2) + ":" + str(self.second).zfill(2) + ":" + str(self.millisecond).zfill(3)

    def add_hours(self, hours):
        new_time = datetime(0, 0, 0, self.hour, self.minute, self.second) + timedelta(hours=hours)
        return Time(new_time.hour, new_time.minute, new_time.second, self.millisecond)

    def add_minutes(self, minutes):
        new_time = datetime(0, 0, 0, self.hour, self.minute, self.second) + timedelta(minutes=minutes)
        return Time(new_time.hour, new_time.minute, new_time.second, self.millisecond)

    def add_seconds(self, seconds):
        new_time = datetime(1, 1, 1, self.hour, self.minute, self.second) + timedelta(seconds=seconds)
        return Time(new_time.hour, new_time.minute, new_time.second, self.millisecond)

    def add_milliseconds(self, milliseconds):
        new_time = datetime(1, 1, 1, self.hour, self.minute, self.second, microsecond=self.millisecond * 1000) + timedelta(milliseconds=milliseconds)
        return Time(new_time.hour, new_time.minute, new_time.second, floor(new_time.microsecond / 1000))

    def total_seconds(self):
        return 60 * 60 * self.hour + 60 * self.minute + self.second