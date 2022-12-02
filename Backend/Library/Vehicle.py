class Car:

    def __init__(self, UID, position=[0, 0]) -> None:
        self.UID = UID
        self.position = position


class AutonmousCar(Car):

    def __init__(self, UID, position=[0, 0]) -> None:
        super().__init__(UID, position)


class HumanCar(Car):

    def __init__(self, UID, position=[0, 0]) -> None:
        super().__init__(UID, position)
