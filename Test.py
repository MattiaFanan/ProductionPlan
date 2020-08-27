import unittest

from pyomo.core import value
from PPBase import PPBase
from PPMultiCommodity import PPMultiCommodity
from ParamGenerator import ParamGenerator
import re


class Test(unittest.TestCase):

    def test_same_solution_base_mc(self):
        # with the stub generator they receives the same params
        p_gen = ParamGeneratorStub()
        base = PPBase(p_gen)
        multi_com = PPMultiCommodity(p_gen)

        base_instance = base.get_solution()
        mc_instance = multi_com.get_solution()

        self.assertEqual(
            base_instance.InitialStock.value,
            mc_instance.InitialStock.value,
            "should have same InitialStock")

        for slot in base_instance.Weeks:
            self.assertEqual(
                value(base_instance.Demand[slot]),
                value(mc_instance.Demand[slot]),
                "should have same demand in slot {}".format(value(slot)))

        self.assertEqual(
                value(base_instance.obj()),
                value(mc_instance.obj()),
                "should have same objective function value".format(value(slot)))


class ParamGeneratorStub(ParamGenerator):

    def init_production_slots(self):
        i = 10
        while i <= 100:
            yield 10
            i = i + 10

    def init_production_cost(self, model, i):
        return 1

    def init_setup_costs(self, model, i):
        return 2

    def init_stocking_cost(self, model, i):
        return 0.5

    def init_demand(self, model, i):
        return 200

    def init_initial_stock(self, model):
        return 50
