from datetime import datetime
import os
import subprocess
from time import sleep

from utils.settings import adb, deviceId, bootTime, applications


def before_app_experiment():
    """Setup test phone before running an experiment.

    This sets some parameters on the tested phone, to ensure a minimum of interferences between experiment runs.
    """
    # Disable auto brightness setting
    subprocess.call("{} -s {} shell settings put system screen_brightness_mode 0".format(adb, deviceId), shell=True)

    # Set a low screen brightness value
    subprocess.call("{} -s {} shell settings put system screen_brightness 1".format(adb, deviceId), shell=True)

    # Set battery level to 100%
    subprocess.call("{} -s {} shell dumpsys battery set level 100".format(adb, deviceId), shell=True)


def before(measure_energy):
    """Setup global parameters before starting experiments.

    This will:
        * let user some time to boot tested phone;
        * push test scenarios to phone;
        * install all tested APKs on tested phone;
        * disables screen sleep;
        * create a directory for each application category.

    This will return the name of the current experiment directory.
    """
    # Let user some time to boot phone
    print("You can boot your phone now.")
    sleep(bootTime)

    # Push test scenarios to phone
    print("\n==> Uploading test scenarios to phone...")
    for app in applications:
        subprocess.call("{} -s {} push {} /data/local/tmp".format(adb, deviceId, app.scenario), shell=True)

    # Create results directories
    now = datetime.now()
    results_dir_name = now.strftime("results_{}_%d-%m-%Y_%H:%M:%S".format("energy" if measure_energy else "system"))
    os.mkdir(results_dir_name)

    for app in applications:
        app_dir = results_dir_name + "/" + app.category
        if not os.path.exists(app_dir):
            os.mkdir(app_dir)

    # Install all applications at once.
    print("\n==> Installing test applications on phone...")
    for app in applications:
        subprocess.call("{} -s {} install {}".format(adb, deviceId, app.apk_path), shell=True)

    # Force the screen to be always on
    subprocess.call("{} -s {} shell svc power stayon true".format(adb, deviceId), shell=True)

    return results_dir_name


def after():
    """Restores global settings modified by before().

    This will:
        * re-enable screen sleep;
        * re-enable screen auto-brightness;
        * uninstall test applications.
    """
    # Allow the screen to be powered off to save battery
    subprocess.call("{} -s {} shell svc power stayon false".format(adb, deviceId), shell=True)

    # Enable auto brightness setting
    subprocess.call("{} -s {} shell settings put system screen_brightness_mode 1".format(adb, deviceId), shell=True)

    # Install all applications at once.
    print("\n==> Uninstalling test applications...")
    for app in applications:
        subprocess.call("{} -s {} uninstall {}".format(adb, deviceId, app.package_name), shell=True)
    print("Done.\n")


def start_scenario(scenariopath, expect_connection_cut=True):
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

    if expect_connection_cut:
        print("Scenario launched.")
