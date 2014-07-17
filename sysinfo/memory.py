import os
import re

def memory():
    return _meminfo("MemTotal")

def free_memory():
    return _meminfo("MemFree") + _meminfo("Cached")

def _meminfo(field):
    meminfo_lines = open("/proc/meminfo").read().split("\n")
    for line in meminfo_lines:
        if line.startswith(field):
            fields = re.split("\s+", line)
            return int(fields[1])
