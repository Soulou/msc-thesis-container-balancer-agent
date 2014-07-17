#!/usr/bin/env python2

from flask import Flask
from flask import request
from flask import Response

from threading import Thread
import sysinfo

from container import Container
from container import ContainerJSONEncoder

import json

app = Flask(__name__)
app.debug = True

@app.route("/containers", methods=['GET'])
def get_containers():
    containers = Container.all()
    return json.dumps(map((lambda container: container.info), containers))

@app.route("/containers", methods=['POST'])
def new_container():
    try:
        service = request.form['service']
    except KeyError:
        return Response("service field should be providen", status=422)

    try:
        port = int(request.form['port'])
        return json.dumps(Container.create(service=service, port=port))
    except KeyError:
        return json.dumps(Container.create(service=service), cls=ContainerJSONEncoder)

@app.route("/container/<container_id>", methods=['GET'])
def get_container(container_id):
    return Response(json.dumps(Container.find(container_id), cls=ContainerJSONEncoder), status=200)

@app.route("/container/<container_id>", methods=['PATCH'])
def update_container(container_id):
    pass

@app.route("/container/<container_id>", methods=['DELETE'])
def delete_container(container_id):
    Container.find(container_id).delete()
    resp = Response(None, status=204)
    return resp

@app.route("/status", methods=["GET"])
def node_status():
    status = {
        "cpus": sysinfo.cpus_usage(),
        "free_memory": sysinfo.free_memory(),
        "memory": sysinfo.memory(),
        "net": sysinfo.net_interfaces_usage(),
        "nb_containers": Container.count()
    }
    return json.dumps(status)

if __name__ == "__main__":
    thread_cpu_monitoring = Thread(target = sysinfo.monitor_cpus, args = ())
    thread_cpu_monitoring.start()
    thread_netdev_monitoring = Thread(target = sysinfo.monitor_netdev, args = ())
    thread_netdev_monitoring.start()
    app.run(host='0.0.0.0')
