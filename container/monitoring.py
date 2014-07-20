from time import sleep
import re
import os
import os.path

def container_usage(cid):
    for container_full_id in _container_cpu_percent.keys():
        if container_full_id.startswith(cid):
            return {
                "cpu": _container_cpu_percent[container_full_id],
                "memory": container_memory(container_full_id),
                "net": _container_net_bytes[container_full_id]
            }
    raise ContainerNotFound

systemd = os.path.isdir("/usr/lib/systemd")

def _get_cgroup_dir(name):
    if systemd:
        return "/sys/fs/cgroup/{}/system.slice".format(name)
    else:
        return "/sys/fs/cgroup/{}/docker".format(name)

if systemd:
    id_regexp = re.compile("docker-[a-f0-9]{64}\.scope")
else:
    id_regexp = re.compile("[a-f0-9]{64}")

_memory_base_dir = _get_cgroup_dir("memory")
_cpuacct_base_dir = _get_cgroup_dir("cpuacct")

_container_cpuacct_prev = {}
_container_cpuacct = {}
_container_cpu_percent = {}

_container_net_prev = {}
_container_net = {}
_container_net_bytes = {}

def monitor_containers():
    while True:
        cgroups = os.listdir(_cpuacct_base_dir)
        for cgroup in cgroups:
            if re.match(id_regexp, cgroup):
                if systemd:
                    cid = cgroup.split("-")[1].split(".")[0]
                else:
                    cid = cgroup

                try:
                    _container_cpuacct_prev[cid] = _container_cpuacct[cid]
                    _container_net_prev[cid] = _container_net[cid]
                except:
                    # new container, first metrics
                    _create_netns_link(cgroup, cid)

                _container_net[cid] = container_network(cid)
                _container_cpuacct[cid] = int(open(_cpuacct_base_dir + "/" + cgroup + "/cpuacct.usage").read())
                try:
                    _container_cpu_percent[cid] = (_container_cpuacct[cid] - _container_cpuacct_prev[cid]) / 10 / 1024 / 1024
                    _container_net_bytes[cid] = {
                        "rx": _container_net[cid]["rx"] - _container_net_prev[cid]["rx"],
                        "tx": _container_net[cid]["tx"] - _container_net_prev[cid]["tx"]
                    }
                except:
                    pass
        sleep(1)

def _create_netns_link(cgroup, cid):
    pid = open("{}/{}/tasks".format(_memory_base_dir, cgroup)).read().split("\n")[0]
    os.system("mkdir -p /var/run/netns")
    os.system("ln -sf /proc/{}/ns/net /var/run/netns/{}".format(pid, cid))

def container_network(cid):
    lines = os.popen("ip netns exec {} netstat -i".format(cid)).read().split("\n")
    for line in lines:
        if line.startswith("eth0"):
            line_split = re.split("\s+", line)
            return {"rx": int(line_split[2]), "tx": int(line_split[6])}

def container_memory(cid):
    if systemd:
        cid = "docker-{}.scope".format(cid)
    return int(open("{}/{}/memory.usage_in_bytes".format(_memory_base_dir, cid)).read())
