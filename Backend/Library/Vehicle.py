class Car:

    def __init__(self, UID, position=[0, 0]) -> None:
        self.UID = UID
        self.position = position

    def get_position(self):
        return self.position


class AutonmousCar(Car):

    def __init__(self, UID, position=[0, 0]) -> None:
        super().__init__(UID, position)


class HumanCar(Car):

    def __init__(self, UID, position=[0, 0]) -> None:
        super().__init__(UID, position)
