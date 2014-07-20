from time import sleep
import re
import os

def cpus_usage():
    return _cpus_usage

_cpus_usage_raw = {}
_cpus_usage = {}
def monitor_cpus():
    while True:
        procstat_lines = open("/proc/stat").read().split("\n")
        for line in procstat_lines:
            m = re.match("^cpu\d+\s.*", line)
            if m:
                split_line = line.split(" ")
                cpu_name = split_line[0]
                current_cpu_usage = int(split_line[1]) + int(split_line[2]) + int(split_line[3])
                try:
                    _cpus_usage[cpu_name] = current_cpu_usage - _cpus_usage_raw[cpu_name]
                except:
                    pass
                _cpus_usage_raw[cpu_name]  = current_cpu_usage
        sleep(1)
