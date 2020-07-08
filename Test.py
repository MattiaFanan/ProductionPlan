import unittest

from pyomo.core import value
from PPBase import PPBase
from PPMCOZero import PPMCOZero
from PPMulltyCommodity import PPMultiCommodity
from ParamGenerator import ParamGenerator


class Test(unittest.TestCase):

    # this test may fail if there are multiple optimal solutions --> change params in stub
    def test_same_solution_base_mc(self):
        # with the stub generator they receives the same params
        p_gen = ParamGeneratorStub()
        base = PPBase(p_gen)
        multi_com = PPMultiCommodity(p_gen)

        base_instance = base.get_solution()
        multi_com_instance = multi_com.get_solution()

        self.assertEqual(
            base_instance.InitialStock.value,
            multi_com_instance.InitialStock.value,
            "should have same demand in InitialStock")

        for slot in base_instance.Weeks:
            self.assertEqual(
                value(base_instance.Demand[slot]),
                value(multi_com_instance.Demand[slot]),
                "should have same demand in slot {}".format(value(slot)))

            self.assertEqual(
                value(base_instance.Production[slot]),
                sum(value(multi_com_instance.Production[slot, i]) for i in base_instance.Weeks),
                "should have same Production in slot {}".format(value(slot)))

            self.assertEqual(
                base_instance.Stock[slot].value,
                sum(value(multi_com_instance.Stock[slot, i]) for i in base_instance.Weeks),
                "should have same Production in slot {}".format(value(slot)))

    def test_same_solution_mc_zero(self):
        # with the stub generator they receives the same params
        p_gen = ParamGeneratorStub()
        zero = PPMCOZero(p_gen)
        multi_com = PPMultiCommodity(p_gen)

        zero_instance = zero.get_solution()
        multi_com_instance = multi_com.get_solution()

        self.assertEqual(
            zero_instance.InitialStock.value,
            multi_com_instance.InitialStock.value,
            "should have same demand in InitialStock")

        for slot in zero_instance.Weeks:
            self.assertEqual(
                value(zero_instance.Demand[slot]),
                value(multi_com_instance.Demand[slot]),
                "should have same demand in slot {}".format(value(slot)))
            for i in zero_instance.Weeks:

                expected = 0
                if i >= slot:
                    expected = value(zero_instance.Production[slot, i])

                self.assertEqual(
                    expected,
                    value(multi_com_instance.Production[slot, i]),
                    "should have same Production in slot {}".format(value(slot)))

            for i in zero_instance.Weeks:

                expected = 0
                if i >= slot:
                    expected = value(zero_instance.Stock[slot, i])

                self.assertEqual(
                    expected,
                    value(multi_com_instance.Stock[slot, i]),
                    "should have same Production in slot {}".format(value(slot)))


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
