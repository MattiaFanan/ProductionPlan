from pyomo.opt import SolverFactory
from timeit import repeat
from PPBase import PPBase
from PPMulltyCommodity import PPMultiCommodity
from ParamGenerator import ParamGenerator

opt = SolverFactory('cplex_persistent')
base_model = PPBase(ParamGenerator())
multi_commodity_model = PPMultiCommodity(ParamGenerator())


def base():
    opt.solve(tee=False)


# extract build_model from timed code --> it's required to rebuild the model because number of slots changes
def init_base():
    base_instance = base_model.build_model().create_instance()
    opt.set_instance(base_instance)


def multi_com():
    opt.solve(tee=False)


def init_multi_com():
    multi_commodity_instance = multi_commodity_model.build_model().create_instance()
    opt.set_instance(multi_commodity_instance)


if __name__ == "__main__":
    for i in range(10):
        print(repeat(stmt=base, setup=init_base, repeat=5, number=1))
        print(repeat(stmt=multi_com, setup=init_multi_com, repeat=5, number=1))
        print("###")
