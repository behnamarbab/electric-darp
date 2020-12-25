from passenger import Passenger
from station import Station
from vehicle import Vehicle

import openpyxl
import random
from pathlib import Path
from copy import deepcopy
import heapq

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

    # TODO:
    def generate_route(self):
        for i in range(GA.r):
            route = []

            pass_raw = [(deepcopy(GA.passengers[j])) for j in range(len(GA.passengers)) if self.chromo[i][j]!=0]
            passengers = [(p.get_expected_time(), p) for p in pass_raw]
            heapq.heapify(passengers)

            # ! O(n*n) -> Optimize it to O(n*Log_n)
            while any([not p[1].is_dropped() for p in passengers]):
                VIP = heapq.heappop(passengers)[1]

                VIP.next_state()
                route.append(VIP.get_station())
                t = VIP.get_expected_time()

                heapq.heappush(passengers, (t, VIP))

            self.routes.append(route)

    # TODO: --------------
    def find_fitness(self):
        pass

    def row_mutate(self, mother: Chromo, x=0.6):
        child = Chromo()
        father = self

        selected_row = random.randint(0, GA.r)

        for r in range(GA.r):
            for c in range(GA.c):
                if r == selected_row:
                    if random.random() < x:
                        child.chromo[r][c] = father.chromo[r][c]
                    else:
                        child.chromo[r][c] = mother.chromo[r][c]
                else:
                    child.chromo[r][c] = father.chromo[r][c]

        self.calibrate(selected_row=selected_row)

        return child

    def column_mutate(self, passenger_ratio, gas_ratio):
        self.pas_column_mutate(passenger_ratio)
        # self.gas_column_mutate(gas_ratio)

    def pas_column_mutate(self, passenger_ratio=0.05):

        if random.random() < passenger_ratio:
            a, b = random.sample(range(0, len(GA.passengers)), 2)
            self.swap_columns(a, b)
        
    def gas_column_mutate(self, gas_ratio):
        for i in range(GA.r):
            for j in range(len(GA.passengers), GA.c):
                if random.random() < gas_ratio:
                    self.swap_bit(i, j)

    def swap_bit(self, i, j):
        self.chromo[i][j] ^= 1

    def swap_columns(self, i, j):
        for r in range(GA.r):
            self.chromo[r][i], self.chromo[r][j] = self.chromo[r][j], self.chromo[r][i]

    def calibrate(self, selected_row=0):
        other_rows = self.chromo[0:selected_row] + self.chromo[selected_row+1: GA.c]
        other_rows_ids = list(range(GA.r))
        other_rows_ids.remove(selected_row)

        for c in range(GA.c):
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
        self.chromo = [random.choices([0, 1], weights=(zeros, ones), k=GA.c) for _ in range(GA.r)]
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
    passengers = []
    vehicles = []
    stations = {}
    gas_stations = []
    r, c = 0, 0

    # Constructor
    def __init__(self, input_file, population_size=100, mutation_ratio=0.05, new_to_old_probability=0.5, passengers_count=5, vehicles_count=3):
        self.input_file = input_file
        self.population_size = population_size
        self.mutation_ratio = mutation_ratio
        self.new_to_old_probability = new_to_old_probability

        self.population = []
        self.new_population = []
        self.selection_probabilities = []

        self.passengers_count = passengers_count
        self.vehicles_count = vehicles_count

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
    def select_for_next_gen(self):
        pass

    def gen_init_population(self):
        for _ in range(self.population_size):
            ch = Chromo()
            ch.gen_random(zeros=GA.r)
            ch.calibrate()
            ch.find_fitness()
            self.population.append(ch)

    @staticmethod
    def generate_station(values, _type):
        _id = values[0]
        _dstop = values[1]
        _q = (_type, values[4])
        _early = values[7]
        _late = values[10]

        st = Station(_id=_id, early=_early, late=_late, dstop=_dstop, _type=_q)
        GA.stations[_id] = st
        if st.type & 2 != 0:
            GA.gas_stations.append(st.id)

        return st
# [Depot] [Gas] [Dropoff/Pickup]
# 001 drop  000 pickup  110 Depot with Gas station

    def parse_input(self):
        xlsx_file = Path(".", "5passenger sample.xlsx")
        wb_object = openpyxl.load_workbook(xlsx_file)
        distance_sheet = wb_object['distance']
        parameters_sheet = wb_object['parameters']
        parameters_values = list(parameters_sheet.values)
        
        # Get the passengars pick-up/drop-off information
        for p in range(1, self.passengers_count+1):
            pick_st = GA.generate_station(parameters_values[p], 0)            
            drop_st = GA.generate_station(parameters_values[p+self.passengers_count], 1)

            passenger = Passenger(p, pick_st, drop_st)
            GA.passengers.append(passenger)

        p = 11
        GA.generate_station(parameters_values[p], 6)
        p = 12
        GA.generate_station(parameters_values[p], 2)

        # Update distances
        for i, row in enumerate(distance_sheet.iter_rows(values_only=True)):
            if i==0:
                continue
            row_values = row
            distances = row_values[1:]
            _id = row_values[0]
            GA.stations[_id].set_distances(distances)

        GA.c = len(GA.stations)
        GA.row = len(GA.vehicles)

    def out(self):
        print("Iterations done!")

    """
        population: [chormo, ...]
        population = generate_first_generation(size, ....)
        new_population = generate_new_generation(population, ...)
        find_fitnesses(new_population) ->
            population = select_based_on_fitness(new_population)
    """
