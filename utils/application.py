class TestedApplication:
    """This is a payload class representing a tested application.

    It carries name of the tested application, relative path (from project root) to associated test scenario, and said
    scenario run time (in seconds).
    """
    def __init__(self, name, scenario, duration):
        self.name = name
        self.scenario = scenario
        self.duration = duration
