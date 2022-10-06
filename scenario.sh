#!/bin/bash


# Make sure the application is installed on your phone.
PACKAGE="tpl.monitoring.firebase"
ACTIVITY="tpl.monitoring.firebase.ScreenSlidePagerActivity"

# Launch app
am start -n $PACKAGE/$ACTIVITY

# Wait a bit to let Monsoon start sampling.
sleep 2


# Swipe left
input swipe 600 500 100 500 100

# Wait few seconds to simulate user waiting
sleep 1

# Swipe left
input swipe 600 500 100 500 100

# Wait few seconds to simulate user waiting
sleep 1

# Swipe left
input swipe 600 500 100 500 100

# Wait few seconds to simulate user waiting
sleep 1

# Swipe left
input swipe 600 500 100 500 100

# Wait few seconds to simulate user waiting
sleep 1

# Swipe right
input swipe 100 500 600 500 100

# Wait few seconds to simulate user waiting
sleep 1

# Swipe right
input swipe 100 500 600 500 100

# Wait few seconds to simulate user waiting
sleep 1

# Swipe right
input swipe 100 500 600 500 100

# Wait few seconds to simulate user waiting
sleep 1

# Swipe right
input swipe 100 500 600 500 100

# Wait few seconds to simulate user waiting
sleep 1

# Back button (to pause/put the app in background)
input keyevent 4

# Wait few seconds to wait until report is sent
sleep 12
