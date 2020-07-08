from numpy.random import randint
from random import uniform


class ParamGenerator:

    def init_production_slots(self):
        i = 10
        while i <= 100:
            yield i
            i = i+10
    
    def init_production_cost(self, model, i):
        return uniform(1, 5)
    
    def init_setup_costs(self, model, i):
        return uniform(10, 20)

    def init_stocking_cost(self, model, i):
        return uniform(1, 5)
    
    def init_demand(self, model, i):
        return uniform(100, 400)
    
    def init_initial_stock(self, model):
        return uniform(0, 100)
