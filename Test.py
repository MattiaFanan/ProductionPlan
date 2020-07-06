import unittest

from pyomo.core import value
from PPBase import PPBase
from PPMulltyCommodity import PPMultiCommodity
from ParamGenerator import ParamGenerator


class Test(unittest.TestCase):

    # this test may fail if there are multiple optimal solutions
    def test_same_solution(self):
        # with the stub generator they receives the same params
        p_gen = ParamGeneratorStub(20, 7, 9)
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


class ParamGeneratorStub(ParamGenerator):

    def __init__(self, weeks, uni_int, uni_double):
        self.weeks = weeks
        self.uni_int = uni_int
        self.uni_double = uni_double

    def get_uniform_int(self, min_val, max_val):
        return self.uni_int

    def get_uniform_double(self, min_val, max_val):
        return self.uni_double

    def get_random_from_list(self, values):
        return self.weeks
