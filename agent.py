#!/usr/bin/env python3

import os

from flask import Flask
from flask import request
from flask import Response

from threading import Thread
import sysinfo

from container import monitor_containers
from container import container_usage
from container import Container
from container import ContainerJSONEncoder

import json

app = Flask(__name__)
app.debug = True


@app.route("/containers", methods=['GET'])
def get_containers():
    containers = Container.all()
    service = request.args.get("service")
    if service != None:
        containers = Container.filter_by_service(containers, service)
    return json.dumps(list(map((lambda container: container.info), containers)))

@app.route("/containers", methods=['POST'])
def new_container():
    try:
        service = request.form['service']
    except KeyError:
        return Response("service field should be providen", status=422)
    try:
        image = request.form['image']
    except KeyError:
        return Response("image field should be providen", status=422)

    try:
        port = int(request.form['port'])
        return json.dumps(Container.create(service=service, port=port, image=image))
    except KeyError:
        return json.dumps(Container.create(service=service, image=image), cls=ContainerJSONEncoder)

@app.route("/container/<container_id>", methods=['GET'])
def get_container(container_id):
    return Response(json.dumps(Container.find(container_id), cls=ContainerJSONEncoder), status=200)

@app.route("/container/<container_id>/status", methods=['GET'])
def get_container_status(container_id):
    try:
        usage = container_usage(container_id)
    except:
        return Response(json.dumps({"error": "not found"}), status=404)
    return json.dumps(usage)

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
    thread_container_monitoring = Thread(target = monitor_containers, args = ())
    thread_container_monitoring.start()
    app.run(host='0.0.0.0', use_reloader=False)
