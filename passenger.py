from enum import Enum
from station import Station

class Status(Enum):
    WAITING = 1
    IN_CAR = 2
    DROPPED = 3

class Passenger:
    def __init__(self, _id, pickup_station:Station, dropoff_station:Station, status=Status.WAITING, punishment=1):
        self.id = _id
        self.punishment = punishment
        self.pickup_station = pickup_station
        self.dropoff_station = dropoff_station
        self.status = status

    def is_waiting(self):
        return self.status==Status.WAITING

    def is_in_car(self):
        return self.status==Status.IN_CAR
    
    def is_dropped(self):
        return self.status==Status.DROPPED

    def next_state(self):
        if self.status == Status.WAITING:
            self.status = Status.IN_CAR
        if self.status == Status.IN_CAR:
            self.status = Status.WAITING

        return self.status

    def get_expected_time(self):
        if self.status == Status.WAITING:
            return self.pickup_station.late
        if self.status == Status.IN_CAR:
            return self.dropoff_station.late
        return 1441

    def get_station(self):
        if self.status == Status.WAITING:
            return self.pickup_station.id
        
        if self.status == Status.IN_CAR:
            return self.dropoff_station.id
        
        else:
            return self.dropoff_station.id

    def __lt__(self, other):
        self.id < other.id