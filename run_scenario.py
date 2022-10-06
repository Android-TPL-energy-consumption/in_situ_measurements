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
    # Let user some time to boot phone
    print("You can boot your phone now.")
    # sleep(60)

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

            # Start sampling
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
    print("Running scenario on phone...")
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
