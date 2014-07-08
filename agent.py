#!/usr/bin/env python2

from flask import Flask
from flask import json
from flask import request
from flask import Response

from container import Container
from container import ContainerJSONEncoder
import traceback

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

if __name__ == "__main__":
    app.run(host='0.0.0.0')
