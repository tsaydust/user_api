from tabnanny import check

import consul
from .single import SingletonMeta
import uuid
import socket
from typing import Tuple, List, Dict
import settings
from dns import asyncresolver, rdatatype


def get_current_ip():
    sock_ip = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock_ip.connect(("8.8.8.8", 80))
    ip = sock_ip.getsockname()[0]
    sock_ip.close()
    return ip


class AddressService:
    def __init__(self, ip: str, port: int):
        self.ip = ip
        self.port = port
        self.count = 0

    def increment(self):
        self.count += 1


class LoadBalancer:
    def __init__(self, addresses: List[Dict[str, int]] = None):
        self.addresses: List[AddressService] = []
        if addresses:
            self.init_addresses(addresses)

    def init_addresses(self, addresses):
        self.addresses.clear()
        for address in addresses:
            self.addresses.append(AddressService(address["ip"], address["port"]))

    def get_address(self) -> Tuple[str | None, int | None]:
        if len(self.addresses) > 0:
            self.addresses.sort(key=lambda address: address.count)
            address = self.addresses[0]
            address.increment()
            return address.ip, address.port
        else:
            return None, None


class CustomConsul(metaclass=SingletonMeta):
    def __init__(self):
        self.consul_host = settings.CONSUL_HOST
        self.consul_dns_port = settings.CONSUL_DNS_PORT
        self.consul_http_port = settings.CONSUL_HTTP_PORT
        self.client = consul.Consul(self.consul_host, self.consul_http_port)
        self.service_id = uuid.uuid4().hex
        self.balancer = LoadBalancer()

    def register(self):
        ip = get_current_ip()
        port = settings.SERVER_PORT
        self.client.agent.service.register(
            name="user_api",
            service_id=self.service_id,
            address=ip,
            port=port,
            tags=['user'],
            check=consul.Check.http(f"http://{ip}:{port}/health", "10s")
        )

    def deregister(self):
        self.client.agent.service.deregister(self.service_id)

    async def fetch_user_service_address(self):
        resolver = asyncresolver.Resolver()
        resolver.nameservers = [self.consul_host]
        resolver.port = self.consul_dns_port

        answer_ip = await resolver.resolve("user_service.service.consul", rdatatype.A)
        answer_port = await resolver.resolve("user_service.service.consul", rdatatype.SRV)

        ips = []
        ports = []

        for i in answer_ip:
            ips.append(i.address)

        for i in answer_port:
            ports.append(i.port)

        user_address = []

        for i, port in enumerate(ports):
            if len(ips) == 1:
                user_address.append({"ip": ips[0], "port": port})
            else:
                user_address.append({"ip": ips[i], "port": port})
        self.balancer.init_addresses(user_address)

    def get_one_address(self) -> Tuple[str | None, int | None]:
        return self.balancer.get_address()
