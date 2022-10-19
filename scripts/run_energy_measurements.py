import subprocess
import threading
from time import sleep

import Monsoon.LVPM as LVPM
import Monsoon.sampleEngine as sampleEngine
import Monsoon.Operations as op
import Monsoon.pmapi as pmapi

from utils.settings import applications, adb, deviceId, runsCount, LVPMSerialNo, deviceVoltage, bootTime


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
    sleep(bootTime)

    # Push test scenarios to phone
    print("\n==> Uploading test scenarios to phone...")
    for app in applications:
        subprocess.call("{} -s {} push {} /data/local/tmp".format(adb, deviceId, app.scenario), shell=True)

    # Install all applications at once.
    print("\n==> Installing test applications on phone...")
    for app in applications:
        subprocess.call("{} -s {} install {}".format(adb, deviceId, app.apk_path), shell=True)

    # Force the screen to be always on
    subprocess.call("{} -s {} shell svc power stayon true".format(adb, deviceId), shell=True)

    # Run scenarios
    for x in range(runsCount):
        for app in applications:
            # Disable auto brigthness setting
            subprocess.call("{} -s {} shell settings put system screen_brightness_mode 0".format(adb, deviceId), shell=True)

            # Set a low screen brightness value
            subprocess.call("{} -s {} shell settings put system screen_brightness 1".format(adb, deviceId), shell=True)

            # Set battery level to 100%
            subprocess.call("{} -s {} shell dumpsys battery set level 100".format(adb, deviceId), shell=True)

            print("\n==> Launching run n°{} with {} application".format(x, app.name))

            # Install application
            # print("====> Installing test application on phone...")
            # subprocess.call("{} -s {} install {}".format(adb, deviceId, app.apk_path), shell=True)

            # Stops sampling after scenario is over.
            monsoon_engine.setStopTrigger(sampleEngine.triggers.GREATER_THAN, app.duration)

            # Launch scenario
            threading.Thread(target=thread_function, args=(app.scenario,)).start()

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

    # Allow the screen to be powered off to save battery
    subprocess.call("{} -s {} shell svc power stayon false".format(adb, deviceId), shell=True)

    # Enable auto brigthness setting
    subprocess.call("{} -s {} shell settings put system screen_brightness_mode 1".format(adb, deviceId), shell=True)

    # Install all applications at once.
    print("\n==> Uninstalling test applications...")
    for app in applications:
        subprocess.call("{} -s {} uninstall {}".format(adb, deviceId, app.package_name), shell=True)
    print("Done.\n")


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
    subprocess.call('{} -s {} shell nohup sh /data/local/tmp/{}'.format(adb, deviceId, scenario), shell=True)
    print("Scenario launched.")


def start_sampling():
    monsoon_engine.startSampling(sampleEngine.triggers.SAMPLECOUNT_INFINITE)


def setup_monsoon():
    """ Sets up Monsoon power monitor configuration.

    This configures Monsoon low-voltage power monitor (LVPM)[1] to provide some current on main channels to power tested
    phone.

    [1]: https://msoon.github.io/powermonitor/LVPM.html
    """
    monsoon = LVPM.Monsoon()
    monsoon.setup_usb(LVPMSerialNo, pmapi.USB_protocol())

    # Basic configuration.
    monsoon.fillStatusPacket()
    monsoon.setVout(deviceVoltage)
    engine = sampleEngine.SampleEngine(monsoon)

    # Disables console output.
    engine.ConsoleOutput(False)

    # Auto mode disables USB connection when sampling starts, and reactivates it when sampling ends.
    monsoon.setUSBPassthroughMode(op.USB_Passthrough.Auto)

    # Stop condition is time (will wait for a scenario to end).
    engine.setTriggerChannel(sampleEngine.channels.timeStamp)

    return engine


# Prepare Monsoon tooling
monsoon_engine = setup_monsoon()
run_all_experiments()
exit(0)
