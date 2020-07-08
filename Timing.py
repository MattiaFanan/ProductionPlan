from pyomo.opt import SolverFactory
from timeit import repeat
from PPBase import PPBase
from PPMulltyCommodity import PPMultiCommodity
from PPMulltyCommodityOptimized import PPMultiCommodityOptimized
from ParamGenerator import ParamGenerator

opt = SolverFactory('cplex_persistent')
base_model = PPBase(ParamGenerator())
multi_commodity_model = PPMultiCommodity(ParamGenerator())
multi_commodity_optimized_model = PPMultiCommodityOptimized(ParamGenerator())


def solve():
    opt.solve(tee=False)


# extract build_model from timed code --> it's required to rebuild the model because number of slots changes
def init_base():
    base_instance = base_model.build_model().create_instance()
    opt.set_instance(base_instance)


# extract build_model from timed code --> it's required to rebuild the model because number of slots changes
def init_optimized():
    multi_commodity_model_optimized_instance = multi_commodity_optimized_model.build_model().create_instance()
    opt.set_instance(multi_commodity_model_optimized_instance)


def init_multi_com():
    multi_commodity_instance = multi_commodity_model.build_model().create_instance()
    opt.set_instance(multi_commodity_instance)


if __name__ == "__main__":
    for i in range(3):
        print("Base: {}".format(repeat(stmt=solve, setup=init_base, repeat=7, number=1)))
        print("MC: {}".format(repeat(stmt=solve, setup=init_multi_com, repeat=7, number=1)))
        print("BMOpt: {}".format(repeat(stmt=solve, setup=init_optimized, repeat=7, number=1)))
        print("###")
