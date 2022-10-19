import os
import subprocess
import threading
from time import sleep

from utils.settings import applications, adb, deviceId, runsCount
from utils.setup import before_app_experiment, before, after, start_scenario

SCRIPTS_ON_PHONE = "/data/local/tmp/"
SAMPLING_TIME_FOR_MEMORY_IN_SECONDS = 1
SAMPLING_TIME_FOR_CPU_IN_SECONDS = 1
MEMINFO_OUTPUT_ON_PHONE = "/data/local/tmp/meminfo.dat"
TOPINFO_OUTPUT_ON_PHONE = "/data/local/tmp/topinfo.dat"
TCPDUMP_OUTPUT_ON_PHONE = '/data/local/tmp/network.pcap'
BUFFER_SIZE_FOR_TCPDUMP = 30000

pid_memory = 0
pid_top = 0


def run_metrics_experiments():
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

    before()

    # Push utility script on phone
    subprocess.call("{} -s {} push {} /data/local/tmp".format(adb, deviceId, "utils/scripts/runcommand.sh"), shell=True)

    # Run scenarios
    for x in range(runsCount):
        for app in applications:
            before_app_experiment()
            print("\n==> Launching run n°{} with {} application".format(x, app.name))

            setup_metrics(app.package_name)

            # Launch scenario
            threading.Thread(target=start_scenario, args=(app.scenario,)).start()

            # Stop sampling after scenario is over
            print("====> Waiting for scenario to end...")
            sleep(app.duration)
            print("====> Scenario is over.")

            # Wait for phone to be reconnected to computer
            sleep(4)

            # Stop the application.
            subprocess.call("{} -s {} shell am force-stop {}".format(adb, deviceId, app.package_name), shell=True)

            # Download metrics and remove associated files from tested phone.
            stop_metrics_processus()
            collect_metrics("{}_{}".format(app.name.replace(" ", "_"), x))

    after()


def setup_metrics(package):
    # Call to meminfo in the android phone (to measure memory)
    subprocess.call("{} shell 'sh {}/runcommand.sh {} \"dumpsys meminfo --local {}| grep TOTAL\" {}' &"
                    .format(
                        adb, SCRIPTS_ON_PHONE, SAMPLING_TIME_FOR_MEMORY_IN_SECONDS, package, MEMINFO_OUTPUT_ON_PHONE
    ),
        shell=True, universal_newlines=True)

    # Get the pid associated to meminfo
    pid_memory = subprocess.check_output(
        adb + " shell ps | grep -w sh |  awk '{print $2}'",
        shell=True, universal_newlines=True
    )
    print("====> Meminfo PID: " + pid_memory)

    # Call to top in the android phone (to measure CPU)
    subprocess.call(
        "{} shell 'top -d {} | grep {} > {}' &".format(
            adb, SAMPLING_TIME_FOR_CPU_IN_SECONDS, package, TOPINFO_OUTPUT_ON_PHONE),
        shell=True, universal_newlines=True
    )

    # Get the pid associated to top
    pid_top = subprocess.check_output(adb + " shell ps | grep -w top |  awk '{print $2}'", shell=True,
                                      universal_newlines=True)
    print("====> Top PID: " + pid_top)

    # TODO tcpdump


def stop_metrics_processus():
    print("====> Stopping metrics processus...")

    # Kill the meminfo process
    subprocess.call("{} shell kill -SIGTERM {}".format(adb, pid_memory), shell=True, universal_newlines=True)

    # Kill the top process
    subprocess.call("{} shell kill -SIGTERM {}".format(adb, pid_top), shell=True, universal_newlines=True)

    # TODO tcpdump


def collect_metrics(output_files_name):
    print("====> Collecting metrics from phone...")

    # Download the meminfo file from the phone
    subprocess.call(adb + " pull " + MEMINFO_OUTPUT_ON_PHONE + " " + output_files_name + '.mem', shell=True)

    # Cleaning format of memory file
    os.system("column -t " + output_files_name + ".mem > " + output_files_name + ".meminfo")
    # Generating file containing PSS information
    os.system("awk '{print $2}' " + output_files_name + ".meminfo > " + output_files_name + ".pss")
    # Removing temp file about memory
    os.system("rm -fr " + output_files_name + ".mem")

    # Delete the file generated by meminfo on phone
    subprocess.call(adb + " shell rm " + MEMINFO_OUTPUT_ON_PHONE, shell=True)

    # Download the top file from the phone
    subprocess.call(adb + " pull " + TOPINFO_OUTPUT_ON_PHONE + " " + output_files_name + ".top", shell=True)

    # Delete the file generated by top from phone
    subprocess.call(adb + " shell rm " + TOPINFO_OUTPUT_ON_PHONE, shell=True)

    # TODO tcpdump


run_metrics_experiments()
exit(0)