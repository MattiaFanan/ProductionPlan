from pyomo.environ import *
from pyomo.opt import SolverFactory
from pyomo.repn.plugins.baron_writer import NonNegativeIntegers, Binary


def obj_rule(model):
	return sum(
		model.SetUpCost[i] * model.SetUp[i]
		+ model.ProductionCost[i] * model.Production[i]
		+ model.Stock[i] * model.StockingCost[i]
		for i in model.Weeks
	)


def stock_rule(model, i):
	return model.Stock[i] == ((model.InitialStock if i == 0 else model.Stock[i-1]) - model.Demand[i] + model.Production[i])


def production_rule(model, i):
	return sum(model.Demand[j] for j in model.Weeks if j >= i) * model.SetUp[i] <= model.Production[i]


def buildmodel(weeks):
	# TODO throw an exception if dim of setup prod demand and stocking dont match

	# Model
	model = AbstractModel()
	# Sets
	model.Weeks = range(weeks)
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


def init_production_cost(model, i):
	l=[0.1, 1.5, 0.75]
	return l[i]


def init_setup_costs(model, i):
	l=[0, 2.5, 2]
	return l[i]


def init_stocking_cost(model, i):
	l=[700, 700, 700]
	return 0 # l[i]


def init_demand(model, i):
	l=[100, 200, 50]
	return l[i]


def init_initial_stock(model):
	return 50


if __name__ == '__main__':
	model = buildmodel(3)
	opt = SolverFactory('cplex_persistent')
	instance = model.create_instance()
	opt.set_instance(instance)
	res = opt.solve(tee=False)
	for w in instance.Weeks:
		print("prod[{}] = {}".format(w, value(instance.Production[w])))
		print("stock[{}] = {}".format(w, value(instance.Stock[w])))
		print("setup[{}] = {}".format(w, value(instance.SetUp[w])))
