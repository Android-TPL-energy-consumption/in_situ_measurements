import subprocess
import threading
import Monsoon.LVPM as LVPM
import Monsoon.sampleEngine as sampleEngine
import Monsoon.Operations as op
import Monsoon.pmapi as pmapi

LVPMSerialNo = 12431
monsoon = LVPM.Monsoon()


def thread_function():
    print("Running scenario on phone...")
    subprocess.call("adb shell sh /data/local/tmp/scenario.sh", shell=True)
    print("Scenario finished.")


def setup_monsoon():
    monsoon.setup_usb(LVPMSerialNo, pmapi.USB_protocol)

    monsoon.fillStatusPacket()
    monsoon.setVout(4)
    engine = sampleEngine.SampleEngine(monsoon)
    engine.enableCSVOutput("results.csv")
    engine.ConsoleOutput(True)
    monsoon.setUSBPassthroughMode(op.USB_Passthrough.Auto)

    monsoon.stopSampling()

    return engine


# Prepare Monsoon tooling
monsoon_engine = setup_monsoon()

# Deploy scenario on phone
print("Deploying scenario on phone...")
subprocess.call("adb push scenario.sh /data/local/tmp", shell=True)
print("Done.")

# Launch scenario
thread = threading.Thread(target=thread_function)
thread.start()

# Start sampling
monsoon_engine.startSampling(sampleEngine.triggers.SAMPLECOUNT_INFINITE)

# Stop sampling after scenario is over
thread.join()
monsoon.stopSampling()
