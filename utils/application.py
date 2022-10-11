class TestedApplication:
    """This is a payload class representing a tested application.

    It carries name of the tested application, relative path (from project root) to associated test scenario, said
    scenario run time (in seconds) and test application package name.
    """
    def __init__(self, name, scenario, duration, package_name):
        self.name = name
        self.scenario = scenario
        self.duration = duration
        self.package_name = package_name
