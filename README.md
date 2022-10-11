# In-situ measurements

This repository holds scripts used to monitor applications' energy consumption on Android. Scripts are:
* `run_scenario.py`: Python script, launched on desktop, that will run all test scenarios on tested phone;
* `scenarios/**.sh`: test scenarios that will run on phone.

### Requirements

* Monsoon low-voltage power monitor: https://msoon.github.io/powermonitor/LVPM.html
* Battery-bypassed phone
* Compiled (release mode) test APKs (you'll find test applications among this organisation's repositories)

### Run

Monsoon requires scripts to be run as `sudo`, otherwise it will throw an error telling it does not have access to LVPM.

```shell
# Install monsoon Python dependency
sudo pip install monsoon

## Run experiments (from project root)
sudo python3 run_scenario.py
```

### External references

* Monsoon API Python documentation: https://msoon.github.io/powermonitor/Python_Implementation/docs/API.pdf
* Original experimentation script: https://github.com/rsain/Android-TPLs/blob/master/scripts/collectEnergyConsumption.py
