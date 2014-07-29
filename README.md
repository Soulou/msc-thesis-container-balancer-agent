# Container balancer agent

## Configuration

-> From environment

* `DOCKER_URL`, default: `file:///var/run/docker.sock`

## Build

```sh
pip install -r requirements.txt
```

## Run

```sh
sudo -E ./agent.py
```

> Root is needed if you want to access docker through the unix socket
> Or your user must be in the docker UNIX user group

## API

* Get current system info of the node itself (CPU, Memory, Net)

`GET /status`

```json
// Code: 200 - OK
// Content-Type: application/json
{
  "cpus": {
    "cpu0": 44,
    "cpu1": 22,
  },
  "memory": 27440000,
  "network": {
    "eth0": {
      "tx": 98765,
      "rx": 12345
    }
  }
}
```

* Get list of all running containers on the node

`GET /containers`

```json
// Code: 200 - OK
// Content-Type: application/json
[
  {
    "Id": "0123456789abcdef",
    "Image": "soulou/msc-thesis-memory-http-service",
    "Ports": [
      {
        "PublicPort": 49127,
        "PrivatePort": 3000
      }
    ],
    "Names": [ "service1-1-837" ],
    "Created": 1723454345,
    "Status": "Up"
  },
  {
    ...
  }
]
```

* Get information about a specific container

`GET /container/:container_id`

```
// Code: 404 - Container not found

// Code: 200 - OK
// Content-Type: application/json

// Docker JSON representation of a container:
// See: http://goo.gl/JrR6f6
```

* Get information about the resource status of a container
  (CPU, Memory, Net)

`GET /container/:container_id/status`

```json
// Code: 404 
//   - Container not found
//   - Data not ready (container launched for less than a second)

// Code 200 - OK
// Content-Type: application/json
{
  "cpu": 44,
  "free_memory": 123456,
  "memory": 2340354,
  "net": {
    "rx": 123456,
    "tx": 123564
  }
}
```

* Create a new container
  Params:
    image: Docker image to use
    service: Name of the service
    port (optional): Choose the given port instead
      of allocating one randomly

`POST /containers`

```
// Code 201 - Container created and started
// Content-Type: application/json

// Docker JSON representation of a container:
// See: http://goo.gl/JrR6f6
```

* Stop and delete the container with the given ID.

`DELETE /container/:container_id`

```
// Code 204 - Container deleted, no content in response
```
