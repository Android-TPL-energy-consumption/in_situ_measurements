import os
import subprocess
from time import sleep

from utils.settings import applications, adb, deviceId, runsCount
from utils.setup import before_app_experiment, before, after, start_scenario

SCRIPTS_ON_PHONE = "/data/local/tmp/"
SAMPLING_TIME_FOR_MEMORY_IN_SECONDS = 1
SAMPLING_TIME_FOR_TEMPERATURE_IN_SECONDS = 1
SAMPLING_TIME_FOR_CPU_IN_SECONDS = 1
MEMINFO_OUTPUT_ON_PHONE = "/data/local/tmp/meminfo.dat"
THERMALINFO_OUTPUT_ON_PHONE = "/data/local/tmp/thermalinfo.dat"
TOPINFO_OUTPUT_ON_PHONE = "/data/local/tmp/topinfo.dat"
TCPDUMP_OUTPUT_ON_PHONE = '/data/local/tmp/network.pcap'
BUFFER_SIZE_FOR_TCPDUMP = 30000


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
    print("\n==> Push utility script on phone...")
    subprocess.call("{} -s {} push {} /data/local/tmp".format(adb, deviceId, "utils/scripts/runcommand.sh"), shell=True)

    # Run scenarios
    for x in range(runsCount):
        for app in applications:
            before_app_experiment()
            print("\n==> Launching run n°{} with {} application".format(x, app.name))

            pids = setup_metrics(app.package_name)

            # Stop sampling after scenario is over
            print("====> Waiting for scenario to end...")

            # Launch scenario
            start_scenario(app.scenario, False)
            print("====> Scenario is over.")

            # Wait for phone to be reconnected to computer
            sleep(4)

            # Stop the application.
            subprocess.call("{} -s {} shell am force-stop {}".format(adb, deviceId, app.package_name), shell=True)

            # Stop metrics sampling on the phone
            stop_metrics_processus(pids)

            # Waiting some time to wait for metrics sampling to end
            sleep(1)

            # Download metrics and remove associated files from tested phone.
            collect_metrics("{}_{}".format(app.name.replace(" ", "_"), x))

    after()


def setup_metrics(package):
    # Call to meminfo in the android phone (to measure memory)
    command = "dumpsys meminfo --local " + package + ' | grep -m 1 TOTAL | sed \\"s/^/\$(date +%s) /\\"'
    subprocess.call("{} -s {} shell \"sh {}/runcommand.sh {} $\'{}\' {}\" &"
                    .format(
                        adb, deviceId,
                        SCRIPTS_ON_PHONE, SAMPLING_TIME_FOR_MEMORY_IN_SECONDS, command, MEMINFO_OUTPUT_ON_PHONE
                    ),
                    shell=True, universal_newlines=True)

    # Get the pid associated to meminfo
    pid_memory = subprocess.check_output(
        adb + " -s " + deviceId + " shell ps -Af | grep ' dumpsys meminfo --local " + package + "' |  awk '{print $2}'",
        shell=True, universal_newlines=True
    )
    print("====> Meminfo PID: " + pid_memory)

    # Call to top in the android phone (to measure CPU)
    subprocess.call(
        "{} -s {} shell -x 'top -o %CPU,%MEM,CMDLINE -d {} | grep {} | grep -v grep > {}' &".format(
            adb, deviceId, SAMPLING_TIME_FOR_CPU_IN_SECONDS, package, TOPINFO_OUTPUT_ON_PHONE),
        shell=True, universal_newlines=True
    )

    # Get the pid associated to top
    pid_top = subprocess.check_output(adb + " -s " + deviceId + " shell pgrep top", shell=True,
                                      universal_newlines=True)
    print("====> Top PID: " + pid_top)

    # Call to thermalservice in the android phone (to measure temperature)
    command = "dumpsys thermalservice | sed -n \\'/Current temperatures from HAL:/,/Current cooling devices from " \
              "HAL:/p\\' | sed \\'1d;\$d\\' | " + 'sed \\"s/^/\$(date +%s) /\\"'
    subprocess.call(
        "{} -s {} shell \"sh {}/runcommand.sh {} $\'{}\' {}\" &".format(
            adb, deviceId, SCRIPTS_ON_PHONE, SAMPLING_TIME_FOR_TEMPERATURE_IN_SECONDS, command,
            THERMALINFO_OUTPUT_ON_PHONE),
        shell=True, universal_newlines=True
    )

    # Get the pid associated to thermalservice
    pid_thermalservice = subprocess.check_output(
        adb + " -s " + deviceId + " shell ps -Af | grep ' dumpsys thermalservice' |  awk '{print $2}'",
        shell=True, universal_newlines=True
    )
    print("====> Thermalservice PID: " + pid_thermalservice)

    # Call to tcpdump in the android phone (to measure network usage)
    tcp_file = open(package + '.tcp_stats', 'w')
    subprocess.call(adb + " -s " + deviceId + " shell su -c tcpdump -s 0 -n -B " + str(BUFFER_SIZE_FOR_TCPDUMP) + " -i wlan0 -w " + TCPDUMP_OUTPUT_ON_PHONE + " &", shell=True, universal_newlines=True, stdout=tcp_file)
    tcp_file.close()

    # Get the pid associated to tcpdump
    pid_tcpdump = subprocess.check_output(adb + " -s " + deviceId + " shell ps -Af | grep tcpdump | grep root | awk '{print $2}'", shell=True, universal_newlines=True)
    print("====> tcpdump PID: " + pid_tcpdump)

    return {
        "pid_memory": pid_memory,
        "pid_top": pid_top,
        "pid_thermalservice": pid_thermalservice,
        "pid_tcpdump": pid_tcpdump
    }


def stop_metrics_processus(pids):
    print("====> Stopping metrics processus...")

    # Kill the meminfo process
    subprocess.call("{} -s {} shell kill -SIGTERM {}".format(adb, deviceId, pids['pid_memory']), shell=True, universal_newlines=True)

    # Kill the top process
    subprocess.call("{} -s {} shell kill -SIGTERM {}".format(adb, deviceId, pids['pid_top']), shell=True, universal_newlines=True)

    # Kill the thermalservice process
    subprocess.call("{} -s {} shell kill -SIGTERM {}".format(adb, deviceId, pids['pid_thermalservice']), shell=True, universal_newlines=True)

    # Kill the tcpdump process
    subprocess.call("{} -s {} shell su -c kill -SIGTERM {}".format(adb, deviceId, pids['pid_tcpdump']), shell=True, universal_newlines=True)


def collect_metrics(output_files_name):
    print("====> Collecting metrics from phone...")

    # Download the meminfo file from the phone
    subprocess.call(adb + " -s " + deviceId + " pull " + MEMINFO_OUTPUT_ON_PHONE + " " + output_files_name + '.mem', shell=True)

    # Cleaning format of memory file
    os.system("column -t " + output_files_name + ".mem > " + output_files_name + ".meminfo")
    # Generating file containing PSS information
    os.system("awk '{print $1, $3}' " + output_files_name + ".meminfo > " + output_files_name + ".pss")
    # Removing temp file about memory
    os.system("rm -fr " + output_files_name + ".mem")

    # Delete the file generated by meminfo on phone
    subprocess.call(adb + " -s " + deviceId + " shell rm " + MEMINFO_OUTPUT_ON_PHONE, shell=True)

    # Download the top file from the phone
    topfilename = output_files_name + ".top"
    topsourcefilename = topfilename + ".source"
    subprocess.call(adb + " -s " + deviceId + " pull " + TOPINFO_OUTPUT_ON_PHONE + " " + topfilename, shell=True)
    # Save original top log file
    os.system("mv " + topfilename + " " + topsourcefilename)
    # Remove color characters from file (https://gist.github.com/stevenh512/2245881)
    os.system("cat \"" + topsourcefilename + "\" | sed -r \"s/\x1B\[([0-9]{1,3}((;[0-9]{1,3})*)?)?[m|K]//g\" > " + topfilename)

    # Delete the file generated by top from phone
    subprocess.call(adb + " -s " + deviceId + " shell rm " + TOPINFO_OUTPUT_ON_PHONE, shell=True)

    # Download the thermal file from the phone
    subprocess.call(adb + " -s " + deviceId + " pull " + THERMALINFO_OUTPUT_ON_PHONE + " " + output_files_name + '.thermalinfo',
                    shell=True)

    # Cleaning format of thermal file
    os.system("column -t " + output_files_name + ".thermalinfo > " + output_files_name + ".temperature")

    # Removing temp file about temperature
    os.system("rm -fr " + output_files_name + ".thermalinfo")

    # Delete the file generated by thermalservice on phone
    subprocess.call(adb + " -s " + deviceId + " shell rm " + THERMALINFO_OUTPUT_ON_PHONE, shell=True)

    # Download the tcpdump file from the phone
    subprocess.call(adb + " -s " + deviceId + " pull " + TCPDUMP_OUTPUT_ON_PHONE + " " + output_files_name + '.pcap', shell=True)

    # Delete the tcpdump file from phone
    subprocess.call(adb + " -s " + deviceId + " shell rm " + TCPDUMP_OUTPUT_ON_PHONE, shell=True)
    print("tcpdump file removed in phone")


run_metrics_experiments()
exit(0)
