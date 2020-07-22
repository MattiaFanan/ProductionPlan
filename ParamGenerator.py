from random import uniform


class ParamGenerator:
    """
    This class is a collection of methods to be passed as parameters generators in the abstract model
    """
    def init_production_slots(self) -> int:
        """
        Generator of ordered values [10,20,...,100]
        :return: an integer used in the abstract model as number of production slot
        """
        i = 10
        while i <= 100:
            yield i
            i = i+10
    
    def init_production_cost(self, model, i) -> float:
        """
        Generates an uniform random value in [1,5] for the production cost parameter in the model
        :param model: the model in which the parameter is being generated
        :param i: id of the production slot to which the cost is referred
        :return: the value for the production cost in the i-th production slot
        """
        return uniform(1, 5)
    
    def init_setup_costs(self, model, i) -> float:
        """
        Generates an uniform random value in [10,20] for the setup cost parameter in the model
        :param model: the model in witch the parameter is being generated
        :param i: id of the production slot to which the cost is referred
        :return: the value for the setup cost in the i-th production slot
        """
        return uniform(10, 20)

    def init_stocking_cost(self, model, i) -> float:
        """
        Generates an uniform random value in [1,5] for the stocking cost parameter in the model
        :param model: the model in witch the parameter is being generated
        :param i: id of the production slot to which the cost is referred
        :return: the value for the stocking cost in the i-th production slot
        """
        return uniform(1, 5)
    
    def init_demand(self, model, i) -> float:
        """
        Generates an uniform random value in [100,400] for the demand parameter in the model
        :param model: the model in witch the parameter is being generated
        :param i: id of the production slot to which the cost is referred
        :return: the value for the demand in the i-th production slot
        """
        return uniform(100, 400)
    
    def init_initial_stock(self, model) -> float:
        """
        Generates an uniform random value in [0,100] for the initial stock parameter in the model
        :param model: the model in witch the parameter is being generated
        :return: the value for the initial stock
        """
        return uniform(0, 100)
