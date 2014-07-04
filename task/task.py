import os
import docker

class ServiceNotFound(Exception):
    pass

class TaskNotFound(Exception):
    pass

class Task:
    service_image = "soulou/msc-thesis-fibo-http-service"
    service_image_id = None
    default_memory = 512 * 1024 * 1024 # 512MB

    def __init__(self, container_data):
        self.info = container_data

    def delete(self):
        c = Task._docker_client()
        c.kill(self.info["Id"])

    @classmethod
    def create(clazz, port):
        c = Task._docker_client()
        # All parameters are not necessary, but it's nice to now which can be changed.
        container = c.create_container(Task.service_image, command=None, hostname=None, user=None,
                detach=False, stdin_open=False, tty=False, mem_limit=Task.default_memory,
                ports=[port], environment=[("PORT=%d" % port)], dns=None, volumes=None,
                volumes_from=None, network_disabled=False, name=None,
                entrypoint=None, cpu_shares=None, working_dir=None,
                memswap_limit=0)

        c.start(container, binds=None, port_bindings={port:port}, lxc_conf=None,
                publish_all_ports=False, links=None, privileged=False,
                dns=None, dns_search=None, volumes_from=None, network_mode=None)

        return container
        

    @classmethod
    def find(clazz, cid):
        c = Task._docker_client()
        try:
            container = c.inspect_container(cid)
        except:
            raise TaskNotFound
        if container['Image'] != Task.service_image_id:
            raise TaskNotFound

        return Task(container)


    @classmethod
    def all(clazz):
        c = Task._docker_client()

        service_containers = []
        containers = c.containers(quiet=False, all=False, trunc=True, latest=False, since=None,
             before=None, limit=-1)
        for container in containers:
            if container['Image'] == _Task.service_image:
                service_containers += Task(container)

        return service_containers

    @classmethod
    def _init_service_image_id(clazz):
        c = Task._docker_client()

        images = c.images(name=Task.service_image, quiet=False, all=False, viz=False)
        if len(images) < 1:
            raise ServiceNotFound()

        Task.service_image_id = images[0]["Id"]

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

if Task.service_image_id == None:
    Task._init_service_image_id()

