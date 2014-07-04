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
