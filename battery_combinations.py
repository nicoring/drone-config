import itertools as it
from collections import Counter

# batteries in series increases cell number
# batteries in parallel increases capacity
# batteries in series same capacity and c_rating
# <= 12 cells two battery types
# >= 12 cells three battery types
# 4 batteries in parallel

class BatteryCombination:
    def __init__(self, num_parallel, batteries):
       self.batteries = batteries
       self.num_parallel = num_parallel

    @property
    def capacity(self):
        return self.num_parallel * self.batteries[0].capacity

    @property
    def cells(self):
        return sum(battery.cells for battery in self.batteries)

    @property
    def max_current(self):
        return self.num_parallel * self.batteries[0].max_current
    
    @property
    def weight(self):
        return self.num_parallel * sum(battery.weight for battery in self.batteries)

    @property
    def battery_name(self):
        return str(self)

    def __str__(self):
        c = Counter(self.batteries)
        name = 'battery combination %d in parallel: ' % self.num_parallel
        for battery, count in c.items():
            name += '%d x %s ' % (count, battery.battery_name)
        return name

    def __repr__(self):
        return str(self)

def valid_combination(combination):
    capacity = combination[0].capacity
    c_rating = combination[0].c_rating
    for battery in combination[1:]:
        if (battery.capacity != capacity or 
            battery.c_rating != c_rating):
            return False
    return True

def combination_generator(batteries, max_battery_types, max_num_batteries):
    combinations = set([])
    all_types = it.combinations(batteries, max_battery_types)
    for types in all_types:
        for i in range(max_num_batteries):
            combinations.update(list(it.combinations_with_replacement(types, i + 1)))
    return combinations

def battery_combinations(edf, batteries):
    max_num_batteries = 5
    max_num_parallel = 4

    if edf.battery_type <= 12:
        max_battery_types = 2
    else:
        max_battery_types = 3

    combinations = combination_generator(batteries, max_battery_types, max_num_batteries)

    for combination in combinations:
        if not valid_combination(combination):
            continue
        cell_sum = sum(battery.cells for battery in combination)
        if not cell_sum == edf.battery_type:
            continue
        for num_parallel in range(max_num_parallel):
            yield BatteryCombination(num_parallel + 1, combination)
