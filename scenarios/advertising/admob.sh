#!/bin/bash

PACKAGE="tpl.ads.banner.admob"
ACTIVITY="tpl.ads.banner.admob.MainActivity"

TIME_IN_SECONDS_TO_LOAD_ADS=40

# Launch app
adb shell am start -n $PACKAGE/$ACTIVITY

# Wait TIME_IN_SECONDS_TO_LOAD_ADS seconds to simulate ads load
sleep TIME_IN_SECONDS_TO_LOAD_ADS