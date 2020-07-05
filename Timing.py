from pyomo.opt import SolverFactory
from timeit import repeat
from PPBase import buildmodel as build_base_model
from PPMulltyCommodity import buildmodel as build_m_c_model

opt = SolverFactory('cplex_persistent')

# todo extract build_model from timed code --> it's required to rebuild the model because number of slots changes


def base():
    opt.solve(tee=False)


def init_base():
    base_model = build_base_model()
    base_instance = base_model.create_instance()
    opt.set_instance(base_instance)


def multi_com():
    opt.solve(tee=False)


def init_multi_com():
    m_c_model = build_m_c_model()
    m_c_instance = m_c_model.create_instance()
    opt.set_instance(m_c_instance)


if __name__ == "__main__":
    for i in range(10):
        print(repeat(stmt=base, setup=init_base, repeat=5, number=1))
        print(repeat(stmt=multi_com, setup=init_multi_com, repeat=5, number=1))
        print("###")
