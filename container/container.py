import os
import docker
import random
import json

class ContainerJSONEncoder(json.JSONEncoder):
    def default(self, o):
        return o.to_json()

class Container:

    def __init__(self, container_data):
        self.info = container_data

    def to_json(self):
        return self.info

    def service(self):
        try:
            return self.info['Name'].split("-")[0][1:]
        except KeyError:
            return self.info['Names'][0].split("-")[0][1:]

    def delete(self):
        c = Container._docker_client()
        c.kill(self.info["Id"])
        c.remove_container(self.info["Id"])

    @classmethod
    def count(clazz):
        c = Container._docker_client()
        containers = c.containers(quiet=True, all=False, trunc=True, latest=False, since=None,
             before=None, limit=-1)
        return len(containers)

    @classmethod
    def create(clazz, service, port=3000, image=None):
        c = Container._docker_client()

        service_containers = Container.all(service=service)
        service_index = 1
        existing_indices = []
        for service_container in service_containers:
            name = service_container.info['Names'][0][1:]
            if not name.startswith(service):
                continue
            existing_indices.append(int(name.split("-")[1]))

        for i in range(len(existing_indices)+1):
            try:
                existing_indices.index(i)
            except ValueError:
                service_index = i
                break

        # All parameters are not necessary, but it's nice to now which can be changed.
        container = c.create_container(image, command=None, hostname=None, user=None,
                detach=False, stdin_open=False, tty=False, mem_limit=0,
                ports=[port], environment=[("PORT={}".format(port))], dns=None, volumes=None,
                volumes_from=None, network_disabled=False, name="{}-{}-{}".format(service, service_index, random.randint(0, 1000)),
                entrypoint=None, cpu_shares=None, working_dir=None,
                memswap_limit=0)

        c.start(container, binds=None, port_bindings={port: None}, lxc_conf=None,
                publish_all_ports=False, links=None, privileged=False,
                dns=None, dns_search=None, volumes_from=None, network_mode=None)

        return c.inspect_container(container)
        

    @classmethod
    def find(clazz, cid):
        c = Container._docker_client()
        try:
            container = c.inspect_container(cid)
        except:
            raise ContainerNotFound

        return Container(container)


    @classmethod
    def all(clazz, service=None):
        c = Container._docker_client()

        service_containers = []
        containers = c.containers(quiet=False, all=False, trunc=True, latest=False, since=None,
             before=None, limit=-1)
        for container in containers:
            if service != None:
                if not container['Names'][0][1:].startswith(service):
                    continue
            service_containers.append(Container(container))

        return service_containers

    @classmethod
    def _docker_client(clazz):
        docker_url = 'unix://var/run/docker.sock'
        try:
            docker_url = os.environ['DOCKER_URL']
        except KeyError:
            pass

        c = docker.Client(base_url='unix://var/run/docker.sock',
                  version='1.12',
                  timeout=10)
        return c

    @classmethod
    def filter_by_service(clazz, containers, service):
        new_containers = []
        for c in containers:
            if c.service() == service:
                new_containers.append(c)
        return new_containers
