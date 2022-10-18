from abc import ABC, abstractmethod, ABCMeta
from ipaddress import IPv4Address, IPv6Address
from typing import Optional, Literal

valid_ip_types = IPv4Address | IPv6Address | str




class ResolverFull(ABC):

    @abstractmethod
    def resolve(self, ip: valid_ip_types, httpx_args: Optional[dict] = None):
        pass

    @abstractmethod
    async def async_resolve(self, ip: valid_ip_types = "", httpx_args: Optional[dict] = None):
        pass


class ResolverLimited(ABC):

    @abstractmethod
    def resolve(self, ip: valid_ip_types, httpx_args: Optional[dict] = None):
        pass

    @abstractmethod
    async def async_resolve(self, ip_version: Literal["ipv4", "ipv6", "dualstack", "combined"],
                            httpx_args: Optional[dict] = None):
        pass
