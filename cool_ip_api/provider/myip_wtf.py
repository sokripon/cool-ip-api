from __future__ import annotations

from datetime import datetime, timedelta
from ipaddress import IPv4Address, IPv6Address
from typing import Optional, Literal

import httpx
from httpx import Response
from pydantic import BaseModel, Field

from cool_ip_api.provider.resolver_abc import ResolverLimited
from cool_ip_api.utils.errors import RateLimitError, QuotaError


class MyIpWTFResponse(BaseModel):
    YourFuckingIPv4Address: Optional[str] = None
    YourFuckingIPv6Address: Optional[str] = None
    __ip: str = Field(None, alias="YourFuckingIPAddress")
    YourFuckingLocation: str
    YourFuckingv4Hostname: Optional[str] = None
    YourFuckingv6Hostname: Optional[str] = None
    __hostname: str = Field(None, alias="YourFuckingHostname")
    YourFuckingISP: str
    YourFuckingTorExit: bool
    YourFuckingCountryCode: str

    class Config:
        allow_population_by_field_name = True

    def __init__(self, **data):
        if data.get("YourFuckingIPAddress"):
            try:
                data["YourFuckingIPv4Address"] = str(IPv4Address(data["YourFuckingIPAddress"]))
                data["YourFuckingv4Hostname"] = data["YourFuckingHostname"]
            except ValueError:
                data["YourFuckingIPv6Address"] = str(IPv6Address(data["YourFuckingIPAddress"]))
                data["YourFuckingv6Hostname"] = data["YourFuckingHostname"]

        super().__init__(**data)


class MyIpWTF(ResolverLimited):
    """
    | Resolver for your own IP address.
    | Website: https://myip.wtf/
    | Limit is a request per minute see https://myip.wtf/automation (ip based check)
    | No commercial use allowed see https://myip.wtf/automation
    | Consider donating to the developer https://myip.wtf/donate
    """
    # TODO: Add check if no ipv6 is available
    _request_limit_amount = 2
    # This is from their website (well its one there but to check for ipv4 and ipv6 we need 2...,
    # but testings shows that it should be fine
    _request_limit_time_period_seconds = 60
    ipv4_url = "https://ipv4.wtfismyip.com/json"
    ipv6_url = "https://ipv6.wtfismyip.com/json"
    dualstack_url = "https://wtfismyip.com/json"

    def __init__(self):
        self.requests_left = self._request_limit_amount
        self.reset_time = datetime.now() + timedelta(seconds=self._request_limit_time_period_seconds)

    def __pre_request(self):
        if self.reset_time < datetime.now():
            self.reset_time = datetime.now() + timedelta(seconds=self._request_limit_time_period_seconds)
            self.requests_left = self._request_limit_amount
        if self.requests_left <= 0:
            raise RateLimitError("You have reached the request limit for this API")

    def __post_request(self, r: Response) -> MyIpWTFResponse:
        if r.status_code == 200:
            self.requests_left -= 1
        else:
            self.requests_left = 0
            self.reset_time = datetime.now() + timedelta(seconds=self._request_limit_time_period_seconds)
            raise QuotaError("You have reached the request limit for this API")
        return MyIpWTFResponse(**r.json())

    def resolve(self, ip_version: Literal["ipv4", "ipv6", "dualstack", "combined"],
                httpx_args: Optional[dict] = None) -> MyIpWTFResponse:
        """
        | Resolves your own IP address.
        :param ip_version: The IP version to resolve. Can be "ipv4", "ipv6", "dualstack"(what your pc prefers) \or "combined"(ipv4 & ipv6).
        :param httpx_args: Arguments to pass to httpx.get()
        :return: API Response as a pydantic model
        :rtype: MyIpWTFResponse
        """
        self.__pre_request()
        if ip_version == "ipv4":
            url = self.ipv4_url
            r = httpx.get(url, **httpx_args or {})
            return self.__post_request(r)
        elif ip_version == "ipv6":
            url = self.ipv6_url
            r = httpx.get(url, **httpx_args or {})
            return self.__post_request(r)
        elif ip_version == "dualstack":
            url = self.dualstack_url
            r = httpx.get(url, **httpx_args or {})
            return self.__post_request(r)
        elif ip_version == "combined":
            ipv4 = self.resolve("ipv4", httpx_args)
            ipv6 = self.resolve("ipv6", httpx_args)

            return MyIpWTFResponse(
                YourFuckingIPv4Address=ipv4.YourFuckingIPv4Address,
                YourFuckingIPv6Address=ipv6.YourFuckingIPv6Address,
                YourFuckingLocation=ipv4.YourFuckingLocation,
                YourFuckingv4Hostname=ipv4.YourFuckingv4Hostname,
                YourFuckingv6Hostname=ipv6.YourFuckingv6Hostname,
                YourFuckingISP=ipv4.YourFuckingISP,
                YourFuckingTorExit=ipv4.YourFuckingTorExit,
                YourFuckingCountryCode=ipv4.YourFuckingCountryCode,
            )

    async def async_resolve(self, ip_version: Literal["ipv4", "ipv6", "dualstack", "combined"],
                            httpx_args: Optional[dict] = None) \
            -> MyIpWTFResponse:
        """
        | Resolves your own IP address.
        :param ip_version: The IP version to resolve. Can be "ipv4", "ipv6", "dualstack"(what your pc prefers) \or "combined"(ipv4 & ipv6).
        :param httpx_args: Arguments to pass to httpx.get()
        :return: API Response as a pydantic model
        :rtype: MyIpWTFResponse
        """
        self.__pre_request()
        if ip_version == "ipv4":
            url = self.ipv4_url
            async with httpx.AsyncClient() as client:
                r = await client.get(url, **httpx_args or {})
                return self.__post_request(r)
        elif ip_version == "ipv6":
            url = self.ipv6_url
            async with httpx.AsyncClient() as client:
                r = await client.get(url, **httpx_args or {})
                return self.__post_request(r)
        elif ip_version == "dualstack":
            url = self.dualstack_url
            async with httpx.AsyncClient() as client:
                r = await client.get(url, **httpx_args or {})
                return self.__post_request(r)
        elif ip_version == "combined":
            ipv4 = await self.async_resolve("ipv4", httpx_args)
            ipv6 = await self.async_resolve("ipv6", httpx_args)
            return MyIpWTFResponse(
                YourFuckingIPv4Address=ipv4.YourFuckingIPv4Address,
                YourFuckingIPv6Address=ipv6.YourFuckingIPv6Address,
                YourFuckingLocation=ipv4.YourFuckingLocation,
                YourFuckingv4Hostname=ipv4.YourFuckingv4Hostname,
                YourFuckingv6Hostname=ipv6.YourFuckingv6Hostname,
                YourFuckingISP=ipv4.YourFuckingISP,
                YourFuckingTorExit=ipv4.YourFuckingTorExit,
                YourFuckingCountryCode=ipv4.YourFuckingCountryCode,
            )
