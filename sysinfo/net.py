import os
import re
from time import sleep

def net_interfaces_usage():
    return _net_interfaces_usage

_net_interfaces_usage_raw = {}
_net_interfaces_usage = {}
def monitor_netdev():
    while True:
        netstat_lines = open("/proc/net/dev").read().split("\n")
        for line in netstat_lines:
            if re.match("^\s*[a-z0-9]+:(\s+\d+)+$", line):
                split_line = re.split("\s+", line)
                if split_line[0]  == "":
                        split_line.pop(0)

                netdev_name = split_line[0][0:-1]

                _net_interfaces_usage[netdev_name] = {"rx": 0, "tx": 0}
                try:
                    _net_interfaces_usage_raw[netdev_name]
                except KeyError:
                    _net_interfaces_usage_raw[netdev_name] = {"rx": 0, "tx": 0}


                current_netdev_rx_usage = int(split_line[1])
                current_netdev_tx_usage = int(split_line[9])
                try:
                    _net_interfaces_usage[netdev_name]["rx"] = current_netdev_rx_usage - _net_interfaces_usage_raw[netdev_name]["rx"]
                    _net_interfaces_usage[netdev_name]["tx"] = current_netdev_tx_usage - _net_interfaces_usage_raw[netdev_name]["tx"]
                except:
                    pass
                _net_interfaces_usage_raw[netdev_name]["rx"] = current_netdev_rx_usage
                _net_interfaces_usage_raw[netdev_name]["tx"] = current_netdev_tx_usage
        sleep(1)
