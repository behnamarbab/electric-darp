class Vehicle:
    def __init__(self, location, time, seats, init_charge=100, onboard_passengers=[]):
        self.location = location
        self.time = time
        self.seats = seats
        self.charge = init_charge
        self.onboard_passengers = onboard_passengers
        self.total_punishment = 0