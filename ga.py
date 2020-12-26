from passenger import Passenger
from station import Station
from vehicle import Vehicle

import openpyxl
import random
import heapq
import math

from enum import Enum
from collections import defaultdict
from pathlib import Path
from copy import deepcopy

# ! This is a bad part of the code, this MUST be changed
# !
DRIVING_PUNISHMENT = 0.1
# !
# ! ----------------------------------------------------
class types(Enum):
    PICKUP = 0
    DROPOFF = 1

class Chromo(object):
    """
        A list consists of details about passangers and vehicles
        route: [ (depot, passengers' starting point, charging stations), passengers destination point, ...]
        all_routes: [route, ...] -> size(all_routes) == number_of_vehicles
        fitness: find_fitness(all_routes)
    """

    def __init__(self, routes=[], fitness=None):
        self.chromo = []
        self.routes = routes
        self.fitness = fitness
        self.key = lambda x:x

    def generate_route(self):
        self.routes = []
        for i in range(0, GA.row_size):
            route = []
            vehicle = deepcopy(GA.vehicles[i])

            passengers = [deepcopy(GA.passengers[j]) for j in range(len(GA.passengers)) if self.chromo[i][j]!=0]
            # passengers = [(p.get_expected_time(), p) for p in passengers_raw]
            heapq.heapify(passengers)

            # ! O(n*n) -> Optimize it to O(n*Log_n)
            while any([not p.is_dropped() for p in passengers]):
                it_was_full = False
                if vehicle.is_full():
                    it_was_full = True
                    VIP = vehicle.get_first_passenger()
                else:
                    VIP = heapq.heappop(passengers)

                if VIP.is_dropped():
                    print('Not good: generate_route()')
                    continue

                vehicle.action(VIP)
                route.append(VIP.id)
                t = VIP.get_expected_time()
                VIP.riding_time.append(t)

                if it_was_full:
                    # The VIP is changed after the above procedure, as we have done some action on it
                    heapq.heapify(passengers)
                else:
                    heapq.heappush(passengers, VIP)

            self.routes.append(route)

    # TODO: --------------
    """
    punishments:
        pickup:
        punishment += PP*(current_time - pickup_late (if > 0))

        dropoff:
        punishment += DP*(current_time - dropoff_late (if > 0))

        riding:
        punishment += RP*(dropoff_time - pickup_time)

        punishment += TDP*total_driving

    Punishment = wp*passenger.punishment + dp*driver.punishment
    """
    def get_fitness(self):
        """
            It is ensured that the route is a feasible route, in the generate route section
        """
        if self.fitness != None:
            return self.fitness
        self.fitness = 0
        for i in range(GA.row_size):
            current_route = self.routes[i]
            vehicle = deepcopy(GA.vehicles[i])
            vehicle.passenger_dict = {x: deepcopy(GA.passengers[x]) for x in self.chromo[i][1:] if self.chromo[i][x]!=0}

            curr_station_id = 0   # Depot is supposed to have index 0
            curr_time = 0
            prev_time = 0
            driving_time = 0
            pid = 0

            for i, pid in enumerate(current_route):
                prev_time = curr_time
                curr_passenger = vehicle.passengers_dict[pid]

                curr_time += GA.get_time_distance(curr_station_id, pid)
                curr_passenger.next_state()
                curr_time = max(curr_time, curr_passenger.get_early())
                curr_passenger.riding_time.append(curr_time)
                
                curr_station_id = pid
                driving_time += curr_time - prev_time
            
            driving_time += GA.get_time_distance(curr_station_id, pid)
            
            for p in vehicle.passenger_dict.values():
                self.fitness += p.get_pickup_punishment() + p.get_dropoff_punishment + p.get_ridein_punishment()
            # ! An ugly part
            self.fitness += driving_time * DRIVING_PUNISHMENT
        
        return self.fitness

    # Mutate based on a row
    def row_mutate(self, mother: Chromo, x=0.6):
        child = Chromo()
        father = self

        selected_row = random.randint(0, GA.row_size)

        for r in range(GA.row_size):
            for c in range(GA.column_size):
                if r == selected_row:
                    if random.random() < x:
                        child.chromo[r][c] = father.chromo[r][c]
                    else:
                        child.chromo[r][c] = mother.chromo[r][c]
                else:
                    child.chromo[r][c] = father.chromo[r][c]

        self.calibrate(selected_row=selected_row)

        return child

    def column_mutate(self, passenger_ratio=0.05, gas_ratio=0.05):
        self.pas_column_mutate(passenger_ratio)
        # self.gas_column_mutate(gas_ratio)

    def pas_column_mutate(self, passenger_ratio=0.05):

        if random.random() < passenger_ratio:
            a, b = random.sample(range(0, len(GA.passengers)), 2)
            self.swap_columns(a, b)
        
    def gas_column_mutate(self, gas_ratio):
        for i in range(GA.row_size):
            for j in range(len(GA.passengers), GA.column_size):
                if random.random() < gas_ratio:
                    self.swap_bit(i, j)

    def swap_bit(self, i, j):
        self.chromo[i][j] ^= 1

    def swap_columns(self, i, j):
        for r in range(GA.row_size):
            self.chromo[r][i], self.chromo[r][j] = self.chromo[r][j], self.chromo[r][i]

    def calibrate(self, selected_row=0):
        other_rows = self.chromo[0:selected_row] + self.chromo[selected_row+1: GA.column_size]
        other_rows_ids = list(range(GA.row_size))
        other_rows_ids.remove(selected_row)

        for c in range(GA.column_size):
            if c < len(GA.passengers):
                if self.chromo[selected_row][c] == 0:
                    if not any([r[c] for r in other_rows]):
                        random_row = random.choice(other_rows_ids)
                        self.chromo[random_row][c] = 1

                elif self.chromo[selected_row][c] == 1:
                    for r in other_rows_ids:
                        self.chromo[r][c] = 0        

        # return

    def gen_random(self, ones=1.00, zeros=1.00):
        self.chromo = [random.choices([0, 1], weights=(zeros, ones), k=GA.column_size) for _ in range(GA.row_size)]
        """
            len([...]) = 12               = random.choices([0, 1], weights=(ones, zeros), k=len(GA.stations)):
            chromo = [], rchoices = [0,1,1,1] 
            chromo = [[0,1,1,1]], rchoices = [1,0,0,1]
            chromo = [ 
                       [0,1,1,1], 
                       [1,0,0,1]
                     ]
        """


class GA:
    passengers = {}
    vehicles = {}
    stations = {}
    gas_stations = []
    r, c = 0, 0

    # Constructor
    def __init__(self, input_file="testinstance", population_size=100, mutation_ratio=0.05, new_to_old_probability=0.5, passengers_count=5, vehicles_count=3, beta=1):
        self.input_file = input_file
        self.population_size = population_size
        self.mutation_ratio = mutation_ratio
        self.new_to_old_probability = new_to_old_probability
        self.beta = beta

        self.population = []
        self.new_population = []
        self.selection_probabilities = []

        self.passengers_count = passengers_count
        self.vehicles_count = vehicles_count
        GA.vehicles = {i: Vehicle(location=0, time=0, seats=2) for i in range(vehicles_count)}

        self.parse_input()

    # the main execution function
    def run(self, iterations=1000, new_gen_size=40):
        self.gen_init_population()

        for _iter in range(iterations):
            self.gen_population(n=new_gen_size)
            # population is updated, probabilities are updated
            self.select_for_next_gen()

        self.out()

    # Todo: Select two random parents
    def select_parents(self):
        ch1, ch2 = Chromo(), Chromo()
        return ch1, ch2

    def gen_population(self, n):
        # Fitnesses can be found
        for _ in range(n):
            p1, p2 = self.select_parents()
            child = p1.row_mutate(mother=p2)
            child.column_mutate()
            self.population.append(child)

    # TODO: Select the survivors to the next generation
    # ! All chromosomes have the same weight according to the oldness or newness of the generation
    def select_for_next_gen(self):
        weights = [math.exp(-self.beta * chromo.get_fitness()) for chromo in self.population]
        self.population = list(random.choices(self.population, weights=weights, k=self.population_size))

    def gen_init_population(self):
        for _ in range(self.population_size):
            ch = Chromo()
            ch.gen_random(zeros=GA.row_size)
            ch.calibrate()
            ch.get_fitness()
            self.population.append(ch)

    @staticmethod
    def generate_passenger(values):
        if type<=1:
            _id = values[0]
            pickup_st_id = values[1]
            dropoff_st_id = values[2]
            pickup_early = values[3]
            pickup_late = values[4]
            dropoff_early = values[5]
            dropoff_late = values[6]
            _dstop = values[7]
            _count = values[9]
            
            pickup_st = deepcopy(GA.stations[pickup_st_id])
            pickup_st.early = pickup_early
            pickup_st.late = pickup_late
            pickup_st.dstop = _dstop
            pickup_st.type = types.PICKUP

            dropoff_st = deepcopy(GA.stations[dropoff_st_id])
            dropoff_st.early = dropoff_early
            dropoff_st.late = dropoff_late
            dropoff_st.dstop = _dstop
            dropoff_st.type = types.PICKUP
            
            passenger = Passenger(_id=_id, count=_count, pickup_station=pickup_st, dropoff_station=dropoff_st)

            return passenger

        return None
# [Depot] [Gas] [Dropoff/Pickup]
# 001 drop  000 pickup  110 Depot with Gas station

    def parse_input(self):
        xlsx_file = Path(".", self.input_file)
        wb_object = openpyxl.load_workbook(xlsx_file)
        distance_sheet = wb_object['5passenger parameters']
        parameters_sheet = wb_object['travel time matrix']
        parameters_values = list(parameters_sheet.values)

        # Update distances
        for i, row in enumerate(distance_sheet.iter_rows(values_only=True)):
            if i==0:
                continue
            row_values = row
            distances = row_values[1:]
            _id = row_values[0]
            GA.stations[_id] = Station(_id)
            GA.stations[_id].set_distances(distances)
        
        # Get the passengars pick-up/drop-off information
        for p in range(1, self.passengers_count+1):
            passenger = GA.generate_passenger(parameters_values[p])
            GA.passengers[passenger.id] = passenger

        GA.column_size = len(GA.passengers)+1
        GA.row_size = len(GA.vehicles)

    def out(self):
        print("Iterations done!")

    @staticmethod
    def get_time_distance(i, j):
        return GA.stations[i].distances[j]

    """
        population: [chormo, ...]
        population = generate_first_generation(size, ....)
        new_population = generate_new_generation(population, ...)
        find_fitnesses(new_population) ->
            population = select_based_on_fitness(new_population)
    """
