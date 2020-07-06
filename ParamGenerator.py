from numpy.random import randint
from random import uniform

class ParamGenerator:

    def get_uniform_int(self, min_val, max_val):
        return randint(min_val, max_val + 1)

    def get_uniform_double(self, min_val, max_val):
        return uniform(min_val, max_val)

    def get_from_iterable(self, values):
        return values.__iter__()

    def get_random_from_list(self, values):
        return values[randint(0, len(values))]
    """
    def init_production_slots(self):
        return randint(1, 10 + 1) * 10
    
    def init_production_cost(self, model, i):
        return uniform(1, 5)
    
    def init_setup_costs(self, model, i):
        return uniform(10, 20)

    def init_stocking_cost(self, model, i):
        return uniform(1, 5)
    
    def init_demand(self, model, i):
        return randint(100, 400 + 1)
    
    def init_initial_stock(self, model):
        return 50
    """