from numpy.random import randint
from random import uniform


def init_production_slots():
    return randint(1, 10 + 1) * 10


def init_production_cost(model, i):
    return uniform(1, 5)


def init_setup_costs(model, i):
    return uniform(10, 20)


def init_stocking_cost(model, i):
    return uniform(1, 5)


def init_demand(model, i):
    return randint(100, 400 + 1)


def init_initial_stock(model):
    return 50
