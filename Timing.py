from pyomo.opt import SolverFactory
from timeit import timeit
from PPBase import buildmodel as build_base_model
from PPMulltyCommodity import buildmodel as build_m_c_model

opt = SolverFactory('cplex_persistent')
base_model = build_base_model()
m_c_model = build_m_c_model()


def base():
    instance = base_model.create_instance()
    opt.set_instance(instance)
    return opt.solve(tee=False)


def multi_com():
    instance = m_c_model.create_instance()
    opt.set_instance(instance)
    return opt.solve(tee=False)


if __name__ == "__main__":
    print(timeit(stmt=base, number=1))
    print(timeit(stmt=multi_com, number=1))
