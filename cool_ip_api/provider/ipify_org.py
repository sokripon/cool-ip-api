from __future__ import annotations

from ipaddress import IPv4Address, IPv6Address
from typing import Optional, Literal

import httpx
from pydantic import BaseModel, Field

from cool_ip_api.provider.resolver_abc import ResolverLimited


class IpifyOrgResponse(BaseModel):
    ipv4: str = None
    ipv6: str = None
    __ip: str = Field(None, alias="ip")

    class Config:
        allow_population_by_field_name = True

    def __init__(self, **data):
        if data.get("ip"):
            try:
                data["ipv4"] = str(IPv4Address(data["ip"]))
            except ValueError:
                data["ipv6"] = str(IPv6Address(data["ip"]))

        super().__init__(**data)


class IpifyOrg(ResolverLimited):
    """
    | Resolver for your own IP address.
    | Website: https://www.ipify.org/
    | Limit is infinite see https://www.ipify.org/
    | Commercial seems allowed? https://ipapi.co/pricing/
    """

    ipv4_url = "https://api4.ipify.org/?format=json"
    ipv6_url = "https://api6.ipify.org/?format=json"
    dualstack_url = "https://api64.ipify.org/?format=json"

    def resolve(self, ip_version: Literal["ipv4", "ipv6", "dualstack", "combined"],
                httpx_args: Optional[dict] = None) -> IpifyOrgResponse:
        """
        | Resolves your own IP address.
        :param ip_version: The IP version to resolve. Can be "ipv4", "ipv6", "dualstack"(what your pc prefers) or "combined"(ipv4 & ipv6).
        :param httpx_args: Arguments to pass to httpx.get()
        :return: API Response as a pydantic model
        :rtype: IpifyOrgResponse
        """
        if ip_version == "ipv4":
            url = self.ipv4_url
            r = httpx.get(url, **httpx_args or {})
            return IpifyOrgResponse(**r.json())
        elif ip_version == "ipv6":
            url = self.ipv6_url
            r = httpx.get(url, **httpx_args or {})
            return IpifyOrgResponse(**r.json())
        elif ip_version == "dualstack":
            url = self.dualstack_url
            r = httpx.get(url, **httpx_args or {})
            return IpifyOrgResponse(**r.json())
        elif ip_version == "combined":
            try:
                ipv4 = self.resolve("ipv4", httpx_args)
            except httpx.ConnectError:
                ipv4 = None
            try:
                ipv6 = self.resolve("ipv6", httpx_args)
            except httpx.ConnectError:
                ipv6 = None
            if ipv4 is None and ipv6 is None:
                raise httpx.ConnectError("Could not resolve any IP address")
            return IpifyOrgResponse(ipv4=ipv4.ipv4 if ipv4 else ipv4, ipv6=ipv6.ipv6 if ipv6 else ipv6)

    async def async_resolve(self, ip_version: Literal["ipv4", "ipv6", "dualstack", "combined"],
                            httpx_args: Optional[dict] = None) \
            -> IpifyOrgResponse | tuple[IpifyOrgResponse, IpifyOrgResponse]:
        """
        | Resolves your own IP address.
        :param ip_version: The IP version to resolve. Can be "ipv4", "ipv6", "dualstack"(what your pc prefers) or "combined"(ipv4 & ipv6).
        :param httpx_args: Arguments to pass to httpx.get()
        :return: API Response as a pydantic model
        :rtype: IpifyOrgResponse
        """
        if ip_version == "ipv4":
            url = self.ipv4_url
            async with httpx.AsyncClient() as client:
                r = await client.get(url, **httpx_args or {})
                return IpifyOrgResponse(**r.json())
        elif ip_version == "ipv6":
            url = self.ipv6_url
            async with httpx.AsyncClient() as client:
                r = await client.get(url, **httpx_args or {})
                return IpifyOrgResponse(**r.json())
        elif ip_version == "dualstack":
            url = self.dualstack_url
            async with httpx.AsyncClient() as client:
                r = await client.get(url, **httpx_args or {})
                return IpifyOrgResponse(**r.json())
        elif ip_version == "combined":
            try:
                ipv4 = await self.async_resolve("ipv4", httpx_args)
            except httpx.ConnectError:
                ipv4 = None
            try:
                ipv6 = await self.async_resolve("ipv6", httpx_args)
            except httpx.ConnectError:
                ipv6 = None
            return IpifyOrgResponse(ipv4=ipv4.ipv4 if ipv4 else ipv4, ipv6=ipv6.ipv6 if ipv6 else ipv6)
