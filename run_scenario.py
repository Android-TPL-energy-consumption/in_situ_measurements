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
runsCount = 5
applications = [
    TestedApplication("Amplitude", "scenarios/monitoring/amplitude.sh"),
    TestedApplication("Firebase", "scenarios/monitoring/firebase.sh"),
    TestedApplication("Amplitude", "scenarios/monitoring/new_relic.sh")
]


def thread_function():
    print("Running scenario on phone...")
    subprocess.call('{} shell nohup sh /data/local/tmp/scenario.sh'.format(adb), shell=True)
    print("Scenario launched.")


def start_sampling():
    monsoon_engine.startSampling(sampleEngine.triggers.SAMPLECOUNT_INFINITE)


def setup_monsoon():
    monsoon.setup_usb(LVPMSerialNo, pmapi.USB_protocol())

    monsoon.fillStatusPacket()
    monsoon.setVout(4)
    engine = sampleEngine.SampleEngine(monsoon)
    engine.enableCSVOutput("results.csv")
    engine.ConsoleOutput(False)
    monsoon.setUSBPassthroughMode(op.USB_Passthrough.Auto)

    engine.setStopTrigger(sampleEngine.triggers.GREATER_THAN, 30)
    engine.setTriggerChannel(sampleEngine.channels.timeStamp)

    return engine


# Prepare Monsoon tooling
monsoon_engine = setup_monsoon()

# Let user some time to boot phone
print("You can boot your phone now.")
sleep(60)

# Deploy scenario on phone
print("Deploying scenario on phone...")
subprocess.call("{} push scenario.sh /data/local/tmp".format(adb), shell=True)
print("Done.")

# Launch scenario
thread = threading.Thread(target=thread_function)
thread.start()

# Start sampling
thread = threading.Thread(target=start_sampling)
thread.start()

# Stop sampling after scenario is over
print("Waiting for scenario to end...")
thread.join()
print("Scenario is over.")

print("Done.")
