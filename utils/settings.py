from utils.application import TestedApplication


# Test phone serial ID (listed in `adb devices`).
deviceId = "R58R11WW16L"

# Test phone battery voltage (usually written on it).
deviceVoltage = 4.4

# Identifier of the Monsoon LVPM.
LVPMSerialNo = 12431

# Since this is run as root, adb must be invoked from its absolute path.
adb = "/opt/android-sdk/platform-tools/adb"

# Number of times all scenarios will be ran.
runsCount = 3

# Tested applications.
applications = [
    TestedApplication("Amplitude", "scenarios/monitoring/amplitude.sh", 30,
                      "tpl.monitoring.amplitude", "apks/monitoring/amplitude.apk"),
    TestedApplication("Firebase", "scenarios/monitoring/firebase.sh", 30,
                      "tpl.monitoring.firebase", "apks/monitoring/firebase.apk"),
    TestedApplication("New Relic", "scenarios/monitoring/new_relic.sh", 30,
                      "tpl.monitoring.newrelic", "apks/monitoring/new-relic.apk")
]
