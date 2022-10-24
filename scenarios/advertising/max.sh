#!/bin/bash

PACKAGE="tpl.ads.banner.max"
ACTIVITY="tpl.ads.banner.max.MainActivity"

TIME_IN_SECONDS_TO_LOAD_ADS=40

# Launch app
adb shell am start -n $PACKAGE/$ACTIVITY

# Wait TIME_IN_SECONDS_TO_LOAD_ADS seconds to simulate ads load
sleep TIME_IN_SECONDS_TO_LOAD_ADS