from pyomo.environ import *
from pyomo.opt import SolverFactory
from pyomo.repn.plugins.baron_writer import NonNegativeIntegers, Binary
from ParamGenerator import *
from termcolor import colored


def obj_rule(model):
    return sum(
        model.ProductionCost[i] * model.Production[i, destination_slot]
        + model.StockingCost[i] * model.Stock[i, destination_slot]
        for i in model.Weeks
        for destination_slot in model.Weeks
        # if destination_slot >= i
    ) + sum(
        model.SetUpCost[i] * model.SetUp[i]
        for i in model.Weeks
    )


def stock_rule(model, i, destination_slot):
    if destination_slot < i:  # we can't stock now for past slots
        return model.Stock[i, destination_slot] == 0

    pre_stocked = 0
    if i == model.Weeks[0] and destination_slot == i:  # initial stock only for demand 1
        pre_stocked = model.InitialStock
    elif i > model.Weeks[0]:  # picks the already stocked value if exists
        pre_stocked = model.Stock[i - 1, destination_slot]

    return model.Stock[i, destination_slot] == (
            pre_stocked
            - (model.Demand[i] if i == destination_slot else 0)  # delta(t)*(- demand(t))
            + model.Production[i, destination_slot]
    )


def production_rule(model, i, destination_slot):
    if destination_slot < i:  # we can't produce now for past slots
        return model.Production[i, destination_slot] == 0

    # if we don't pay the setup we don't produce
    # demand(x) is big_M for production(i,x)
    return model.Demand[destination_slot] * model.SetUp[i] >= model.Production[i, destination_slot]


def buildmodel():
    # TODO throw an exception if dim of setup prod demand and stocking dont match

    # Model
    model = AbstractModel()
    # Sets
    model.Weeks = range(1, init_production_slots() + 1)
    # variables
    model.Production = Var(model.Weeks, model.Weeks, domain=NonNegativeIntegers, initialize=0)
    model.SetUp = Var(model.Weeks, domain=Binary, initialize=0)
    model.Stock = Var(model.Weeks, model.Weeks, domain=NonNegativeIntegers, initialize=0)
    # params
    model.InitialStock = Param(initialize=init_initial_stock, default=0)
    model.ProductionCost = Param(model.Weeks, initialize=init_production_cost, default=0)
    model.SetUpCost = Param(model.Weeks, initialize=init_setup_costs, default=0)
    model.StockingCost = Param(model.Weeks, initialize=init_stocking_cost, default=0)
    model.Demand = Param(model.Weeks, initialize=init_demand, default=0)
    # objective
    model.obj = Objective(rule=obj_rule)
    # constraints
    model.pc = Constraint(model.Weeks, model.Weeks, rule=production_rule)
    model.sc = Constraint(model.Weeks, model.Weeks, rule=stock_rule)
    return model


if __name__ == '__main__':
    model = buildmodel()
    opt = SolverFactory('cplex_persistent')
    instance = model.create_instance()
    opt.set_instance(instance)
    res = opt.solve(tee=False)

    print("prod each column a production-slot row destination-slot")
    for w in instance.Weeks:
        print(
            *(
                (
                    colored(round(value(instance.Production[i, w])), "green")
                    if i == w
                    else round(value(instance.Production[i, w]))
                    for i in instance.Weeks))
            , sep="|\t"
        )

    print("setup")
    print(*(round(value(instance.SetUp[w])) for w in instance.Weeks), sep="|\t")

    print("stock each column a production-slot row destination-slot")
    for w in instance.Weeks:
        print(
            *(
                (
                    colored(round(value(instance.Stock[i, w])), "green")
                    if i == w
                    else round(value(instance.Stock[i, w]))
                    for i in instance.Weeks))
            , sep="|\t"
        )

    print("parameters")

    print("A0 = {}".format(round(value(instance.InitialStock))))

    for w in instance.Weeks:
        print("slot{} # demand = {} # P-cost = {} # S-cost = {}".format(
            w, value(instance.Demand[w]), value(instance.ProductionCost[w]), value(instance.StockingCost[w])
        ))
