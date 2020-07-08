from pyomo.opt import SolverFactory
from timeit import repeat
from PPBase import PPBase
from PPMCOZero import PPMCOZero
from PPMulltyCommodity import PPMultiCommodity
from PPMulltyCommodityOptimized import PPMultiCommodityOptimized
from ParamGenerator import ParamGenerator

opt = SolverFactory('cplex_persistent')
base_abstract_model = PPBase(ParamGenerator())
multi_commodity_abstract_model = PPMultiCommodity(ParamGenerator())
multi_commodity_optimized_abstract_model = PPMultiCommodityOptimized(ParamGenerator())
zero_abstract_model = PPMCOZero(ParamGenerator())


def solve_zero():
    zero_instance = zero_model.create_instance()
    opt.set_instance(zero_instance)
    opt.solve(tee=False)


def solve_base():
    base_instance = base_model.create_instance()
    opt.set_instance(base_instance)
    opt.solve(tee=False)


def solve_optimized():
    multi_commodity_model_optimized_instance = multi_commodity_optimized_model.create_instance()
    opt.set_instance(multi_commodity_model_optimized_instance)
    opt.solve(tee=False)


def solve_multi_com():
    multi_commodity_instance = multi_commodity_model.create_instance()
    opt.set_instance(multi_commodity_instance)
    opt.solve(tee=False)


if __name__ == "__main__":
    reps = 5
    for i in range(10):
        # build_model changes the number of production slots
        base_model = base_abstract_model.build_model()
        multi_commodity_model = multi_commodity_abstract_model.build_model()
        multi_commodity_optimized_model = multi_commodity_optimized_abstract_model.build_model()
        zero_model = zero_abstract_model.build_model()
        # creates new instance with same number of production slots and solves it --> for #reps times
        print("Base: {}".format(repeat(stmt=solve_base, repeat=reps, number=1)))
        print("MC: {}".format(repeat(stmt=solve_multi_com, repeat=reps, number=1)))
        print("BMOpt: {}".format(repeat(stmt=solve_optimized, repeat=reps, number=1)))
        print("Zero: {}".format(repeat(stmt=solve_zero, repeat=reps, number=1)))
        print("###")


