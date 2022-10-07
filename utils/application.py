class TestedApplication:
    """This is a payload class representing a tested application.

    It carries name of the tested application, and relative path (from project root) to associated test scenario.
    """
    def __init__(self, name, scenario):
        self.name = name
        self.scenario = scenario
