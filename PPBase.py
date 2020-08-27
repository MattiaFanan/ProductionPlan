"""
This module contains the class PPBase
can be executed as a demo script that solves a random initialized problem and prints the result
"""
from pyomo.environ import *
from pyomo.opt import SolverFactory
from pyomo.repn.plugins.baron_writer import NonNegativeReals, Binary
from ParamGenerator import ParamGenerator


class PPBase:
    """
    This class manages the model for a standard O(n) variables production planning problem
    """
    def __init__(self, param_generator):
        self.param_generator = param_generator
        self.week_iter = self.param_generator.init_production_slots()

    # objective function to be passed to the model
    @staticmethod
    def __obj_rule(model):
        return sum(
            model.SetUpCost[i] * model.SetUp[i]
            + model.ProductionCost[i] * model.Production[i]
            + model.Stock[i] * model.StockingCost[i]
            for i in model.Weeks
        )

    # rule about stocking quantities to be passed to the model
    @staticmethod
    def __stock_rule(model, i):
        return model.Stock[i] == ((model.InitialStock if i == model.Weeks[1] else model.Stock[i - 1]) - model.Demand[i]
                                  + model.Production[i])

    # rule about production quantities to be passed to the model
    @staticmethod
    def __production_rule(model, i):
        return sum(model.Demand[j] for j in model.Weeks if j >= i) * model.SetUp[i] >= model.Production[i]

    def build_model(self) -> AbstractModel:
        """
        Builds the abstract model for the production planning problem
        :return: the built abstract model
        """
        # Model
        model = AbstractModel()
        # Sets
        model.Weeks = RangeSet(next(self.week_iter))
        # Variables
        model.Production = Var(model.Weeks, domain=NonNegativeReals)
        model.SetUp = Var(model.Weeks, domain=Binary)
        model.Stock = Var(model.Weeks, domain=NonNegativeReals)
        # Params
        model.InitialStock = Param(
            initialize=lambda mod: self.param_generator.init_initial_stock(mod),
            default=0)

        model.ProductionCost = Param(
            model.Weeks,
            initialize=lambda mod, i: self.param_generator.init_production_cost(mod, i),
            default=0)

        model.SetUpCost = Param(
            model.Weeks,
            initialize=lambda mod, i: self.param_generator.init_setup_costs(mod, i),
            default=0)

        model.StockingCost = Param(
            model.Weeks,
            initialize=lambda mod, i: self.param_generator.init_stocking_cost(mod, i),
            default=0)

        model.Demand = Param(
            model.Weeks,
            initialize=lambda mod, i: self.param_generator.init_demand(mod, i),
            default=0)
        # Objective
        model.obj = Objective(rule=self.__obj_rule)
        # Constraints
        model.pc = Constraint(model.Weeks, rule=self.__production_rule)
        model.sc = Constraint(model.Weeks, rule=self.__stock_rule)
        return model

    def get_solution(self):
        """
        helper method that generates and solves an instance of the production planning problem
        :return: the solved instance
        """
        model = self.build_model()
        opt = SolverFactory('cplex_persistent')
        instance = model.create_instance()
        opt.set_instance(instance)
        result = opt.solve(tee=False)
        return instance


if __name__ == '__main__':

    ins = PPBase(ParamGenerator()).get_solution()

    for w in ins.Weeks:
        print("slot{} # prod = {} # stock = {} # setup = {}".format(
            w, value(ins.Production[w]), value(ins.Stock[w]), value(ins.SetUp[w])
        ))

    print("parameters")

    print("A0 = {}".format(value(ins.InitialStock)))

    for w in ins.Weeks:
        print("slot{} # demand = {} # P-cost = {} # S-cost = {}".format(
            w, value(ins.Demand[w]), value(ins.ProductionCost[w]), value(ins.StockingCost[w])
        ))
