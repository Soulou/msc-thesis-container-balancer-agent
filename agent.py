#!/usr/bin/env python2

from flask import Flask
from flask import json
from flask import request
from flask import Response

from  task import Task
import traceback

app = Flask(__name__)
app.debug = True

@app.route("/tasks", methods=['GET'])
def get_tasks():
    tasks = Task.all()
    return json.dumps(tasks)

@app.route("/tasks", methods=['POST'])
def new_task():
    port = request.form['port']
    return json.dumps(Task.create(int(port)))

@app.route("/task/<task_id>", methods=['PATCH'])
def update_task(task_id):
    pass

@app.route("/task/<task_id>", methods=['DELETE'])
def delete_task(task_id):
    Task.find(task_id).delete()
    resp = Response(None, status=204)
    return resp

if __name__ == "__main__":
    app.run()
