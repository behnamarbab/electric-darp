from passenger import Passenger
import heapq

class Vehicle:
    def __init__(self, location, time, seats, init_charge=100, passengers_dict={}):
        self.location = location
        self.time = time
        self.seats = seats
        self.charge = init_charge
        self.passengers_dict = passengers_dict
        self.onboard_passengers = []
        self.total_punishment = 0

    def action(self, passenger:Passenger):
        passenger.next_state()

        if passenger.is_in_car():
            heapq.heappush(self.onboard_passengers, passenger)
            # self.passengers_list.append(passenger)

        elif passenger.is_dropped():
            self.onboard_passengers.remove(passenger)
            heapq.heapify(self.onboard_passengers)

    def is_full(self):
        return len(self.onboard_passengers) >= self.seats

    def get_first_passenger(self):
        return self.onboard_passengers[0]