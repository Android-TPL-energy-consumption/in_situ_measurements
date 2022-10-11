class TestedApplication:
    """This is a payload class representing a tested application.

    It carries name of the tested application, relative path (from project root) to associated test scenario, said
    scenario run time (in seconds), test application package name and path to tested application's APK file.
    """
    def __init__(self, name, scenario, duration, package_name, apk_path):
        self.name = name
        self.scenario = scenario
        self.duration = duration
        self.package_name = package_name
        self.apk_path = apk_path
