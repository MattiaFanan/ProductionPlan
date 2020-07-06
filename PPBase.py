from pyomo.environ import *
from pyomo.opt import SolverFactory
from pyomo.repn.plugins.baron_writer import NonNegativeIntegers, Binary
from ParamGenerator import ParamGenerator

class PPBase:

    def __init__(self, param_generator):
        self.param_generator = param_generator
        self.week_list = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]

    @staticmethod
    def obj_rule(model):
        return sum(
            model.SetUpCost[i] * model.SetUp[i]
            + model.ProductionCost[i] * model.Production[i]
            + model.Stock[i] * model.StockingCost[i]
            for i in model.Weeks
        )

    @staticmethod
    def stock_rule(model, i):
        return model.Stock[i] == ((model.InitialStock if i == model.Weeks[1] else model.Stock[i - 1]) - model.Demand[i]
                                  + model.Production[i])

    @staticmethod
    def production_rule(model, i):
        return sum(model.Demand[j] for j in model.Weeks if j >= i) * model.SetUp[i] >= model.Production[i]

    def build_model(self):

        # Model
        model = AbstractModel()
        # Sets
        model.Weeks = RangeSet(self.param_generator.get_random_from_list(self.week_list))
        # variables
        model.Production = Var(model.Weeks, domain=NonNegativeIntegers, initialize=0)
        model.SetUp = Var(model.Weeks, domain=Binary, initialize=0)
        model.Stock = Var(model.Weeks, domain=NonNegativeIntegers, initialize=0)
        # params
        model.InitialStock = Param(
            initialize=lambda mod: self.param_generator.get_uniform_int(10, 100),
            default=0)

        model.ProductionCost = Param(
            model.Weeks,
            initialize=lambda mod, i: self.param_generator.get_uniform_double(1, 5),
            default=0)

        model.SetUpCost = Param(
            model.Weeks,
            initialize=lambda mod, i: self.param_generator.get_uniform_double(10, 20),
            default=0)

        model.StockingCost = Param(
            model.Weeks,
            initialize=lambda mod, i: self.param_generator.get_uniform_double(1, 5),
            default=0)

        model.Demand = Param(
            model.Weeks,
            initialize=lambda mod, i: self.param_generator.get_uniform_int(100, 400),
            default=0)
        # objective
        model.obj = Objective(rule=self.obj_rule)
        # constraints
        model.pc = Constraint(model.Weeks, rule=self.production_rule)
        model.sc = Constraint(model.Weeks, rule=self.stock_rule)
        return model

    def get_solution(self):
        model = self.build_model()
        opt = SolverFactory('cplex_persistent')
        instance = model.create_instance()
        opt.set_instance(instance)
        res = opt.solve(tee=False)
        return instance


if __name__ == '__main__':

    instance = PPBase(ParamGenerator()).get_solution()

    for w in instance.Weeks:
        print("slot{} # prod = {} # stock = {} # setup = {}".format(
            w, value(instance.Production[w]), value(instance.Stock[w]), value(instance.SetUp[w])
        ))

    print("parametri")

    print("A0 = {}".format(value(instance.InitialStock)))

    for w in instance.Weeks:
        print("slot{} # demand = {} # P-cost = {} # S-cost = {}".format(
            w, value(instance.Demand[w]), value(instance.ProductionCost[w]), value(instance.StockingCost[w])
        ))
