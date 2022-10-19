import subprocess
import threading
from time import sleep

import Monsoon.sampleEngine as sampleEngine

from utils.settings import applications, adb, deviceId, runsCount
from utils.setup import before_app_experiment, before, after, start_scenario
from utils.monsoon import setup_monsoon


def run_all_experiments():
    """Runs all experiments at once.

    This will run experiments on tested applications in a round-robin fashion, to
    avoid applications to take any benefit from caches.

    You can tune experimentation by updating `runsCount` and `applications` global
    variables.

    Here's what this method does in detail:
        * leave some time to user to boot up tested phone;
        * upload all test scenarios at once to tested phone;
        * run scenarios.
    """

    before()

    # Run scenarios
    for x in range(runsCount):
        for app in applications:
            before_app_experiment()
            print("\n==> Launching run n°{} with {} application".format(x, app.name))

            # Install application
            # print("====> Installing test application on phone...")
            # subprocess.call("{} -s {} install {}".format(adb, deviceId, app.apk_path), shell=True)

            # Stops sampling after scenario is over.
            monsoon_engine.setStopTrigger(sampleEngine.triggers.GREATER_THAN, app.duration)

            # Launch scenario
            threading.Thread(target=start_scenario, args=(app.scenario,)).start()

            # Start sampling (disables USB connection)
            monsoon_engine.enableCSVOutput("{}_{}.csv".format(app.name, x))
            thread = threading.Thread(target=start_sampling)
            thread.start()

            # Stop sampling after scenario is over
            print("====> Waiting for scenario to end (will throw since phone is disconnected on sampling start)...")
            thread.join()
            print("====> Scenario is over.")

            # Wait for phone to be reconnected to computer
            sleep(4)

            # Stop the application.
            subprocess.call("{} -s {} shell am force-stop {}".format(adb, deviceId, app.package_name), shell=True)

            # Uninstall application
            # print("====> Uninstalling test application...")
            # subprocess.call("{} -s {} uninstall {}".format(adb, deviceId, app.package_name), shell=True)

    after()


def start_sampling():
    monsoon_engine.startSampling(sampleEngine.triggers.SAMPLECOUNT_INFINITE)


# Prepare Monsoon tooling
monsoon_engine = setup_monsoon()
run_all_experiments()
exit(0)
