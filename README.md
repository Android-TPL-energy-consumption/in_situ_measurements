# In-situ measurements

This repository holds scripts used to monitor applications' energy consumption on Android. Scripts are:
* `**.py`: Python scripts, launched on desktop, that will run all test scenarios on tested phone;
* `scenarios/**.sh`: test scenarios that will run on phone.

### Requirements

* Monsoon low-voltage power monitor: https://msoon.github.io/powermonitor/LVPM.html
* Battery-bypassed phone
* Compiled (release mode) test APKs (you'll find test applications among this organisation's repositories)

### Setup

Before launching script, you might want to edit some of its parameters, which are located in `utils/settings.py`:

```python
# Test phone serial ID (listed in `adb devices`).
# This allows you to run experiments while other devices are plugged-in to your computer.
deviceId = ""

# Test phone battery voltage (usually written on it).
# This directly influences current furnished by power monitor to the test phone.
deviceVoltage = 4.4

# Identifier of the Monsoon LVPM.
# This is written in the back of the power monitor.
LVPMSerialNo = 12431

# Since script is ran as root, adb must be invoked from its absolute path.
adb = "/opt/android-sdk/platform-tools/adb"

# Number of times all scenarios will be run.
runsCount = 2

# Tested applications.
# You must provide name of the application, relative path to test scenario, duration in seconds of said scenario, test 
# application package and path to test application APK file.
applications = [
    TestedApplication("Amplitude", "scenarios/monitoring/amplitude.sh", 30,
                      "tpl.monitoring.amplitude", "apks/monitoring/amplitude.apk"),
    TestedApplication("Firebase", "scenarios/monitoring/firebase.sh", 30,
                      "tpl.monitoring.firebase", "apks/monitoring/firebase.apk"),
    TestedApplication("New Relic", "scenarios/monitoring/new_relic.sh", 30,
                      "tpl.monitoring.newrelic", "apks/monitoring/new-relic.apk")
]

# Time (in seconds) left to the user to boot the phone before measurements start.
bootTime = 90
```

### Run

Monsoon requires scripts to be run as `sudo`, otherwise it will throw an error telling it does not have access to LVPM.

```shell
# Install monsoon Python dependency
sudo pip install monsoon

## Run experiments (from project root)
sudo python3 run_energy_measurements.py
```

### External references

* Monsoon API Python documentation: https://msoon.github.io/powermonitor/Python_Implementation/docs/API.pdf
* Original experimentation script: https://github.com/rsain/Android-TPLs/blob/master/scripts/collectEnergyConsumption.py
