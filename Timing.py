"""
Script that prints execution time in function of time slots to optimize
for both linear-base and quadratic-multi commodity production planning models
"""
from typing import Callable

import matplotlib.pyplot as plt
import numpy as np
from pyomo.opt import SolverFactory
from timeit import timeit
from PPBase import PPBase
from PPMultiCommodity import PPMultiCommodity
from ParamGenerator import ParamGenerator

# problems will be solved with cplex
opt = SolverFactory('cplex_persistent')
# instantiate classes for problems model management
base_abstract_model = PPBase(ParamGenerator())
multi_commodity_abstract_model = PPMultiCommodity(ParamGenerator())


def modified_repeat(untimed_pre_stmt: Callable[..., any], timed_stmt: Callable[..., any], repeat: int) -> np.ndarray:
    """
    Measures how much time the statement takes to be executed
    :param untimed_pre_stmt: untimed part of the statement executed '':param repeat'' times
    :param timed_stmt: timed part of the statement executed '':param repeat'' times
    :param repeat: number of times the statement will be executed
    :return: array of time measures
    """
    executions_array = np.zeros(repeat)
    for iteration in range(repeat):
        untimed_pre_stmt()
        # takes time only for the timed Callable
        executions_array[iteration] = timeit(stmt=timed_stmt, number=1)
    return executions_array


# helper method to be passed as timed statement to modified_repeat
def __solve() -> None:
    opt.solve(tee=False)


# helper setup method for multi commodity problem to be passed as timed statement to modified_repeat
def __init_multi_commodity():
    multi_commodity_instance = multi_commodity_model.create_instance()
    opt.set_instance(multi_commodity_instance)


# helper setup method for base problem to be passed as timed statement to modified_repeat
def __init_base():
    base_instance = base_model.create_instance()
    opt.set_instance(base_instance)


if __name__ == "__main__":
    reps = 100
    # x axe representation to be printed by pyplot
    x = np.arange(10, 110, 10)

    # y axes representation to be printed by pyplot
    # every cell will contain the average of all the timing iterations
    y_base = np.zeros(10)
    y_multi_commodity = np.zeros(10)

    for i in range(10):
        # build_model changes the number of production slots
        base_model = base_abstract_model.build_model()
        multi_commodity_model = multi_commodity_abstract_model.build_model()
        # creates new instances with same number of production slots and solves it --> for #reps times
        y_base[i] = np.average(
            modified_repeat(untimed_pre_stmt=__init_base, timed_stmt=__solve, repeat=reps))
        y_multi_commodity[i] = np.average(
            modified_repeat(untimed_pre_stmt=__init_multi_commodity, timed_stmt=__solve, repeat=reps))

    # plots and shows the results
    plt.plot(x, y_base, label="base")
    plt.plot(x, y_multi_commodity, label="multi commodity")
    plt.xlabel("# production slots")
    plt.ylabel("solving time")
    plt.legend(loc="upper left")
    plt.show()



