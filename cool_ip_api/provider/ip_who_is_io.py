from __future__ import annotations

from typing import Optional

import httpx
from pydantic import BaseModel

from cool_ip_api.provider.resolver_abc import ResolverFull, valid_ip_types


class Flag(BaseModel):
    img: str
    emoji: str
    emoji_unicode: str


class Connection(BaseModel):
    asn: int
    org: str
    isp: str
    domain: str


class Timezone(BaseModel):
    id: str
    abbr: str
    is_dst: bool
    offset: int
    utc: str
    current_time: str


class IPWhoIsIoResponse(BaseModel):
    ip: str
    success: bool
    type: str
    continent: str
    continent_code: str
    country: str
    country_code: str
    region: str
    region_code: str
    city: str
    latitude: float
    longitude: float
    is_eu: bool
    postal: str
    calling_code: str
    capital: str
    borders: str
    flag: Flag
    connection: Connection
    timezone: Timezone


class IPWhoIsIo(ResolverFull):
    """
    | Resolver for IP addresses.
    | Website: https://ipwhois.io/
    | Limit is 10000 requests per month (api key based check)
    | No commercial use allowed see https://ipwhois.io/pricing
    """
    # TODO: Premium API support
    # TODO: Add timings
    # TODO: Add error handling

    base_url = "https://ipwho.is/"

    def resolve(self, ip: valid_ip_types = "", httpx_args: Optional[dict] = None) -> IPWhoIsIoResponse:
        """
        | Resolves an IP address.
        :param ip: The IP address to resolve. If not provided, the IP address of the client is used.
        :param httpx_args: Arguments to pass to httpx.get()
        :return: API Response as a pydantic model
        :rtype: IPWhoIsIoResponse
        """
        url = f"{self.base_url}{ip}"

        r = httpx.get(url, **httpx_args or {})
        return IPWhoIsIoResponse(**r.json())

    async def async_resolve(self, ip: valid_ip_types = "", httpx_args: Optional[dict] = None) -> IPWhoIsIoResponse:
        """
        | Resolves an IP address.
        :param ip: The IP address to resolve. If not provided, the IP address of the client is used.
        :param httpx_args: Arguments to pass to httpx.get()
        :return: API Response as a pydantic model
        :rtype: IPWhoIsIoResponse
        """
        url = f"{self.base_url}{ip}"

        async with httpx.AsyncClient() as client:
            r = await client.get(url, **httpx_args or {})
            return IPWhoIsIoResponse(**r.json())
