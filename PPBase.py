from pyomo.environ import *
from pyomo.opt import SolverFactory
from pyomo.repn.plugins.baron_writer import NonNegativeIntegers, Binary
from ParamGenerator import *


def obj_rule(model):
    return sum(
        model.SetUpCost[i] * model.SetUp[i]
        + model.ProductionCost[i] * model.Production[i]
        + model.Stock[i] * model.StockingCost[i]
        for i in model.Weeks
    )


def stock_rule(model, i):
    return model.Stock[i] == ((model.InitialStock if i == model.Weeks[0] else model.Stock[i - 1]) - model.Demand[i] +
                              model.Production[i])


def production_rule(model, i):
    return sum(model.Demand[j] for j in model.Weeks if j >= i) * model.SetUp[i] >= model.Production[i]


def buildmodel():
    # TODO throw an exception if dim of setup prod demand and stocking dont match

    # Model
    model = AbstractModel()
    # Sets
    model.Weeks = range(1, init_production_slots() + 1)
    # variables
    model.Production = Var(model.Weeks, domain=NonNegativeIntegers, initialize=0)
    model.SetUp = Var(model.Weeks, domain=Binary, initialize=0)
    model.Stock = Var(model.Weeks, domain=NonNegativeIntegers, initialize=0)
    # params
    model.InitialStock = Param(initialize=init_initial_stock, default=0)
    model.ProductionCost = Param(model.Weeks, initialize=init_production_cost, default=0)
    model.SetUpCost = Param(model.Weeks, initialize=init_setup_costs, default=0)
    model.StockingCost = Param(model.Weeks, initialize=init_stocking_cost, default=0)
    model.Demand = Param(model.Weeks, initialize=init_demand, default=0)
    # objective
    model.obj = Objective(rule=obj_rule)
    # constraints
    model.pc = Constraint(model.Weeks, rule=production_rule)
    model.sc = Constraint(model.Weeks, rule=stock_rule)
    return model


def get_solution():
    model = buildmodel()
    opt = SolverFactory('cplex_persistent')
    instance = model.create_instance()
    opt.set_instance(instance)
    res = opt.solve(tee=False)
    return instance


if __name__ == '__main__':
    instance = get_solution()
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
