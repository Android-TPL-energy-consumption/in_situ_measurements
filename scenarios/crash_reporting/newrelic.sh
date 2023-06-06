#!/bin/bash

PACKAGE="tpl.crashreporting.newrelic"
ACTIVITY="tpl.crashreporting.newrelic.MainActivity"

# Launch app
am start -n $PACKAGE/$ACTIVITY

# Wait few seconds to simulate user waiting
sleep 3


## Click button
input tap 360 713


# Sleep some time (expecting that information is sent to the server)
sleep 3

# Close Android message about the crash by clicking outside it
input tap 500 500

# Wait few seconds to wait until report is sent
sleep 12
