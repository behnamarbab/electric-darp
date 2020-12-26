from enum import Enum
from station import Station

class Status(Enum):
    WAITING = 1
    IN_CAR = 2
    DROPPED = 3

class Passenger:
    def __init__(self, _id, count:int, pickup_station:Station, dropoff_station:Station, status=Status.WAITING, pick_wait_punish=5, drop_wait_punish=5, ridein_punish=1):
        self.id = _id
        self.count = count
        self.pickup_station = pickup_station
        self.dropoff_station = dropoff_station
        self.riding_time = []
        self.status = status
        self.PP = pick_wait_punish
        self.DP = drop_wait_punish
        self.RP = ridein_punish

        self.punishment = 0

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

    def get_station_id(self):
        if self.status == Status.WAITING:
            return self.pickup_station.id
        if self.status == Status.IN_CAR:
            return self.dropoff_station.id        
        else:
            return self.dropoff_station.id

    def get_pickup_time(self):
        return self.riding_time[0]

    def get_dropoff_time(self):
        return self.riding_time[1]

    def get_early(self):
        if self.status in [Status.WAITING, Status.IN_CAR]:
            return self.pickup_station.early
        return self.dropoff_station.early
                                                                            # !: Set the riding times
    # Set the punishment after we have done any action with the passenger
    def set_punishment(self, cur_time):
        if self.status == Status.IN_CAR:
            self.punishment += self.PP * max(0, cur_time - self.pickup_station.late)

        elif self.status == Status.DROPPED:
            self.punishment += self.DP * max(0, cur_time - self.dropoff_station.late)
            self.punishment += self.RP * (self.riding_time[1] - self.riding_time[0])
        
        return self.punishment

    def get_pickup_punishment(self):
        return self.PP * max(0, self.get_pickup_time() - self.pickup_station.late)

    def get_dropoff_punishment(self):
        return self.DP * max(0, self.get_dropoff_time() - self.dropoff_station.late)

    def get_ridein_punishment(self):
        return self.RP * (self.get_dropoff_time() - self.get_pickup_time())
    
    def __lt__(self, other):
        if self.is_dropped() and not other.is_dropped():
            return False
        elif not self.is_dropped() and other.is_dropped():
            return True
        return self.get_expected_time() < other.get_expected_time()
        # if len(self.riding_time) == 0 and len(other.riding_time) == 0:
        #     return self.get_expected_time() < other.get_expected_time()
        # if len(self.riding_time) == 0:
        #     return False
        # if len(other.riding_time) == 0:
        #     return True
        # return self.riding_time[-1] < other.riding_time[-1]