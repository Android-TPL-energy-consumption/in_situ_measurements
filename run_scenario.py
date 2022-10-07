import subprocess
import threading
from time import sleep

import Monsoon.LVPM as LVPM
import Monsoon.sampleEngine as sampleEngine
import Monsoon.Operations as op
import Monsoon.pmapi as pmapi

from utils.application import TestedApplication

LVPMSerialNo = 12431
monsoon = LVPM.Monsoon()
adb = "/opt/android-sdk/platform-tools/adb"
runsCount = 2
applications = [
    TestedApplication("Amplitude", "scenarios/monitoring/amplitude.sh"),
    TestedApplication("Firebase", "scenarios/monitoring/firebase.sh"),
    TestedApplication("New Relic", "scenarios/monitoring/new_relic.sh")
]


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

    # Let user some time to boot phone
    print("You can boot your phone now.")
    sleep(60)

    # Push test scenarios to phone
    print("\n==> Uploading test scenarios to phone...")
    for app in applications:
        subprocess.call("{} push {} /data/local/tmp".format(adb, app.scenario), shell=True)

    # Run scenarios
    for x in range(runsCount):
        for app in applications:
            print("\n==> Launching experiment n°{} with {} application".format(x, app.name))

            # Launch scenario
            threading.Thread(target=thread_function, args=(app.scenario,)).start()

            # Start sampling (disables USB connection)
            monsoon_engine.enableCSVOutput("{}_{}.csv".format(app.name, x))
            thread = threading.Thread(target=start_sampling)
            thread.start()

            # Stop sampling after scenario is over
            print("Waiting for scenario to end...")
            thread.join()
            print("Scenario is over.")

            # Wait for phone to be reconnected to computer
            sleep(4)


def thread_function(scenariopath):
    """Starts input scenario on tested phone.

    Gets scenario file name from input parameter (which is desktop scenario local path), and
    sends an adb command to tested phone, for it to run given scenario.

    Since USB connection between desktop and tested phone is shut down when sampling starts,
    this launches test scenario using the nohup command[1].

    [1]: https://linuxhint.com/how_to_use_nohup_linux/
    """
    print("Running scenario on phone...")

    # scenariopath is local relative path (e.g. scenarios/monitoring/amplitude.sh),
    # so we extract file name from it (e.g. amplitude.sh).
    scenario = scenariopath.split("/")[-1]
    subprocess.call('{} shell nohup sh /data/local/tmp/{}'.format(adb, scenario), shell=True)
    print("Scenario launched.")


def start_sampling():
    monsoon_engine.startSampling(sampleEngine.triggers.SAMPLECOUNT_INFINITE)


def setup_monsoon():
    monsoon.setup_usb(LVPMSerialNo, pmapi.USB_protocol())

    monsoon.fillStatusPacket()
    monsoon.setVout(4)
    engine = sampleEngine.SampleEngine(monsoon)
    engine.ConsoleOutput(False)
    monsoon.setUSBPassthroughMode(op.USB_Passthrough.Auto)

    engine.setStopTrigger(sampleEngine.triggers.GREATER_THAN, 30)
    engine.setTriggerChannel(sampleEngine.channels.timeStamp)

    return engine


# Prepare Monsoon tooling
monsoon_engine = setup_monsoon()
run_all_experiments()
exit(0)
