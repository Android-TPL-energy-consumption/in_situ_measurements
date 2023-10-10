import subprocess
import threading
from time import sleep
from datetime import datetime
import sys

import Monsoon.sampleEngine as sampleEngine

from run_metrics_measurements import setup_metrics, stop_metrics_processus, collect_metrics
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

    global pids
    now = datetime.now()
    print(now.strftime("Started experiments at %d-%m-%Y %H:%M:%S."))

    results_dir = before(measure_energy)

    # Push utility script on phone
    print("\n==> Push utility script on phone...")
    subprocess.call("{} -s {} push {} /data/local/tmp".format(adb, deviceId, "utils/scripts/runcommand.sh"), shell=True)

    # Run scenarios
    for x in range(runsCount):
        for app in applications:
            before_app_experiment()
            print("\n==> Launching run n°{} with {} application".format(x, app.name))

            if not measure_energy:
                pids = setup_metrics(app.package_name)

            # Stops sampling after scenario is over.
            else:
                monsoon_engine.setStopTrigger(sampleEngine.triggers.GREATER_THAN, app.duration)
            print("====> Waiting for scenario to end...")

            # Launch scenario
            if measure_energy:
                threading.Thread(target=start_scenario, args=(app.scenario,)).start()

                # Start sampling (disables USB connection)
                monsoon_engine.enableCSVOutput("{}/{}/{}_{}.csv".format(results_dir, app.category, app.name, x))
                thread = threading.Thread(target=start_sampling)
                thread.start()

                # Stop sampling after scenario is over
                print("====> Waiting for scenario to end (will throw since phone is disconnected on sampling start)...")
                thread.join()

            else:
                start_scenario(app.scenario, False)

            print("====> Scenario is over.")
            # Wait for phone to be reconnected to computer
            sleep(4)

            # Stop the application.
            subprocess.call("{} -s {} shell am force-stop {}".format(adb, deviceId, app.package_name), shell=True)

            # Stop metrics sampling on the phone
            if not measure_energy:
                stop_metrics_processus(pids)

            # Waiting some time to wait for metrics sampling to end
            sleep(3)

            # Download metrics and remove associated files from tested phone.
            if not measure_energy:
                collect_metrics("{}/{}/{}_{}".format(results_dir, app.category, app.name.replace(" ", "_"), x))

    after()


def start_sampling():
    monsoon_engine.startSampling(sampleEngine.triggers.SAMPLECOUNT_INFINITE)


# Two script configurations:
#   * run energy measurements without system metrics
#   * run system metrics measurements without energy measurement
measure_energy = True
if len(sys.argv) > 1 and sys.argv[1] == "-system":
    measure_energy = False

if measure_energy:
    print("This will record energy consumption of the smartphone.")
else:
    print("This will record system metrics of the smartphone.")


# Prepare Monsoon tooling
monsoon_engine = setup_monsoon(measure_energy)

run_all_experiments()
exit(0)
