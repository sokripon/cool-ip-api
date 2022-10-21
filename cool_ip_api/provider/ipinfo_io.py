from __future__ import annotations

from typing import Optional

import httpx
from pydantic import BaseModel

from cool_ip_api.provider.resolver_abc import ResolverFull, valid_ip_types


class IPInfoIoResponse(BaseModel):
    ip: str
    hostname: Optional[str]
    city: str
    region: str
    country: str
    loc: str
    org: str
    postal: str
    timezone: str


class IPInfoIo(ResolverFull):
    """
    | Resolver for IP addresses.
    | Website: https://ipinfo.io/
    | Limit is 50000 requests per month (api key based check)
    | No commercial use allowed see https://ipinfo.io/pricing
    """
    # TODO: Premium API support
    # TODO: Add error handling

    base_url = "https://ipinfo.io/"

    def __init__(self, api_key: str):
        self.api_key = api_key

    def resolve(self, ip: valid_ip_types = "", httpx_args: Optional[dict] = None) -> IPInfoIoResponse:
        ip = ip or ""
        url = f"{self.base_url}{ip}?token={self.api_key}"

        r = httpx.get(url, **httpx_args or {})
        return IPInfoIoResponse(**r.json())

    async def async_resolve(self, ip: valid_ip_types = "", httpx_args: Optional[dict] = None) -> IPInfoIoResponse:
        ip = ip or ""
        url = f"{self.base_url}{ip}"

        async with httpx.AsyncClient() as client:
            r = await client.get(url, **httpx_args or {})
            return IPInfoIoResponse(**r.json())

