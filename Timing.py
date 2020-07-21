import matplotlib.pyplot as plt
import numpy as np
from pyomo.opt import SolverFactory
from timeit import timeit
from PPBase import PPBase
from PPMultiCommodity import PPMultiCommodity
from ParamGenerator import ParamGenerator

opt = SolverFactory('cplex_persistent')
base_abstract_model = PPBase(ParamGenerator())
multi_commodity_abstract_model = PPMultiCommodity(ParamGenerator())


def modified_repeat(untimed_pre_stmt, timed_stmt, repeat):
    executions_array = np.zeros(repeat)
    for i in range(repeat):
        untimed_pre_stmt()
        executions_array[i] = timeit(stmt=timed_stmt, number=1)
    return executions_array


def solve():
    opt.solve(tee=False)


def init_multi_commodity():
    multi_commodity_instance = multi_commodity_model.create_instance()
    opt.set_instance(multi_commodity_instance)


def init_base():
    base_instance = base_model.create_instance()
    opt.set_instance(base_instance)


if __name__ == "__main__":
    reps = 100
    x = np.arange(10, 110, 10)

    y_base = np.zeros(10)
    y_multi_commodity = np.zeros(10)

    for i in range(10):
        # build_model changes the number of production slots
        base_model = base_abstract_model.build_model()
        multi_commodity_model = multi_commodity_abstract_model.build_model()
        # creates new instance with same number of production slots and solves it --> for #reps times
        y_base[i] = np.average(
            modified_repeat(untimed_pre_stmt=init_base, timed_stmt=solve, repeat=reps))
        y_multi_commodity[i] = np.average(
            modified_repeat(untimed_pre_stmt=init_multi_commodity, timed_stmt=solve, repeat=reps))

    plt.plot(x, y_base, label="base")
    plt.plot(x, y_multi_commodity, label="multi commodity")

    plt.xlabel("# production slots")
    plt.ylabel("solving time")
    plt.legend(loc="upper left")
    plt.show()



