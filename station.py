class Station:
    def __init__(self, _id, early=None, late=None, dstop=None, _type=0):
        self.id = _id
        self.early = early
        self.late = late
        self.dstop = dstop
        self.distances = []
        self.type = _type # 1- Passenger ride on    2- Passenger drop off   3- Gas      4- Depot 

    def set_distances(self, distances):
        self.distances = distances

    def __lt__(self, other):
        return self.id < other.id
