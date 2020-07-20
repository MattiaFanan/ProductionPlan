from pyomo.environ import *
from pyomo.opt import SolverFactory
from pyomo.repn.plugins.baron_writer import Binary, NonNegativeReals
from ParamGenerator import ParamGenerator
from termcolor import colored


class PPMultiCommodity:

    def __init__(self, param_generator):
        self.param_generator = param_generator
        self.week_iter = self.param_generator.init_production_slots()

    @staticmethod
    def _obj_rule(model):
        return sum(
            model.ProductionCost[i] * model.Production[i, destination_slot]
            + model.StockingCost[i] * model.Stock[i, destination_slot]
            for (i, destination_slot) in model.SourceDestinationIndex
            # if destination_slot >= i
        ) + sum(
            model.SetUpCost[i] * model.SetUp[i]
            for i in model.Weeks
        )

    @staticmethod
    def _stock_rule(model, i, destination_slot):
        pre_stocked = 0
        if i == model.Weeks[1] and destination_slot == i:  # initial stock only for demand 1
            pre_stocked = model.InitialStock
        elif i > model.Weeks[1]:  # picks the already stocked value if exists
            pre_stocked = model.Stock[i - 1, destination_slot]

        return model.Stock[i, destination_slot] == (
                pre_stocked
                - (model.Demand[i] if i == destination_slot else 0)  # delta(t)*(- demand(t))
                + model.Production[i, destination_slot]
        )
    @staticmethod
    def _zero_stock_rule(model, i,  destination_slot):
        return model.Stock[i, destination_slot] == 0 if i == destination_slot else Constraint.Feasible

    @staticmethod
    def _production_rule(model, i, destination_slot):

        # if we don't pay the setup we don't produce
        # demand(x) is big_M for production(i,x)
        return model.Demand[destination_slot] * model.SetUp[i] >= model.Production[i, destination_slot]

    @staticmethod
    def source_destination_filter(model, source, destination):
        return source <= destination

    def build_model(self):

        # Model
        model = AbstractModel()
        # Sets
        model.Weeks = RangeSet(next(self.week_iter))
        model.SourceDestinationIndex = Set(
            initialize=model.Weeks * model.Weeks,
            filter=self.source_destination_filter)
        # variables
        model.Production = Var(model.SourceDestinationIndex, domain=NonNegativeReals)
        model.SetUp = Var(model.Weeks, domain=Binary)
        model.Stock = Var(model.SourceDestinationIndex, domain=NonNegativeReals)
        # params
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
        # objective
        model.obj = Objective(rule=self._obj_rule)
        # constraints
        model.pc = Constraint(model.SourceDestinationIndex, rule=self._production_rule)
        model.sc = Constraint(model.SourceDestinationIndex, rule=self._stock_rule)
        model.zs = Constraint(model.SourceDestinationIndex, rule=self._zero_stock_rule)
        return model

    def get_solution(self):
        model = self.build_model()
        opt = SolverFactory('cplex_persistent')
        instance = model.create_instance()
        opt.set_instance(instance)
        res = opt.solve(tee=False)
        return instance


if __name__ == '__main__':

    instance = PPMultiCommodity(ParamGenerator()).get_solution()

    print("prod each column a production-slot row destination-slot")
    for w in instance.Weeks:
        print(
            *(
                (
                    (
                        colored(value(instance.Production[i, w]), "green")
                        if i == w
                        else value(instance.Production[i, w])
                    )
                    if (i, w) in instance.SourceDestinationIndex
                    else "x"
                    for i in instance.Weeks))
            , sep="|\t"
        )

    print("setup")
    print(*(round(value(instance.SetUp[w])) for w in instance.Weeks), sep="\t")

    print("stock each column a production-slot row destination-slot")
    for w in instance.Weeks:
        print(
            *(
                (
                    (
                        colored(value(instance.Stock[i, w]), "green")
                        if i == w
                        else value(instance.Stock[i, w])
                    )
                    if (i, w) in instance.SourceDestinationIndex
                    else "x"
                    for i in instance.Weeks))
            , sep="|\t"
        )

    print("parameters")

    print("A0 = {}".format(value(instance.InitialStock)))

    for w in instance.Weeks:
        print("slot{} # demand = {} # P-cost = {} # S-cost = {}".format(
            w, value(instance.Demand[w]), value(instance.ProductionCost[w]), value(instance.StockingCost[w])
        ))