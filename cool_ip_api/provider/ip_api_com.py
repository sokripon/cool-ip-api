# Site: https://ip-api.com/
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Literal
from typing import Optional

import httpx
from httpx import Response
from pydantic import BaseModel, Field

from cool_ip_api.provider.resolver_abc import ResolverFull, valid_ip_types
from cool_ip_api.utils.errors import RateLimitError


class IPAPIComResponse(BaseModel):
    status: str
    message: Optional[str]
    continent: str
    continent_code: str = Field(alias='continentCode')
    country: str
    country_code: str = Field(alias='countryCode')
    region: str
    region_name: str = Field(alias='regionName')
    city: str
    district: str
    zip: str
    lat: float
    lon: float
    timezone: str
    offset: int
    currency: str
    isp: str
    org: str
    as_: str = Field(alias='as')
    asname: str
    reverse: str
    mobile: bool
    proxy: bool
    hosting: bool
    query: str


class IPAPICom(ResolverFull):
    """
    | Resolver for IP address.
    | Website: https://ip-api.com/
    | Limit is 45 requests per minute (ip based check)
    | No commercial use allowed see https://members.ip-api.com/#pricing
    """
    # TODO: Premium API support
    # TODO: Batch API support
    # TODO: Add better error handling
    # Sadly the API doesn't provide an ACCURATE way to check the remaining requests, so we have to do it ourselves

    base_url = "http://ip-api.com/"
    localizations = Literal["en", "de", "es", "fr", "ja", "pt-BR", "ru", "zh-CN"]
    _request_limit_amount = 45
    _request_limit_time_period_seconds = 60

    def __init__(self):
        self.requests_left = self._request_limit_amount
        self.reset_time = datetime.now() + timedelta(seconds=self._request_limit_time_period_seconds)

    def __pre_request(self):
        if self.reset_time < datetime.now():
            self.reset_time = datetime.now() + timedelta(seconds=self._request_limit_time_period_seconds)
            self.requests_left = self._request_limit_amount
        if self.requests_left <= 0:
            raise RateLimitError("You have reached the request limit for this API")

    def __post_request(self, r: Response) -> IPAPIComResponse:
        if r.headers.get("x-rl") == "0":
            self.requests_left = 0
        if r.status_code == 200:
            self.requests_left -= 1
        else:
            self.requests_left = 0
        return IPAPIComResponse(**r.json())

    def resolve(self, ip: valid_ip_types = "", httpx_args: Optional[dict] = None,
                localization: localizations = "en") -> IPAPIComResponse:
        """
        | Resolves an IP address.
        :param ip: The IP address to resolve. If not provided, the IP address of the client is used.
        :param httpx_args: Arguments to pass to httpx.get()
        :param localization: The localization of the response. Defaults to "en".
        :return: API Response as a pydantic model
        :rtype: IPAPIComResponse
        """

        url = f"{self.base_url}json/{ip}?fields=66846719&lang={localization}"  # 66846719 is symbolic for all fields

        self.__pre_request()
        r = httpx.get(url, **httpx_args or {})
        return self.__post_request(r)

    async def async_resolve(self, ip: valid_ip_types = "", httpx_args: Optional[dict] = None,
                            localization: localizations = "en") -> IPAPIComResponse:
        """
        | Resolves an IP addresses.
        :param ip: The IP address to resolve. If not provided, the IP address of the client is used.
        :param httpx_args: Arguments to pass to httpx.get()
        :param localization: The localization of the response. Defaults to "en".
        :return: API Response as a pydantic model
        :rtype: IPAPIComResponse
        """
        url = f"{self.base_url}json/{ip}?fields=66846719&lang={localization}"  # 66846719 is symbolic for all fields

        self.__pre_request()
        async with httpx.AsyncClient() as client:
            r = await client.get(url, **httpx_args or {})
            return self.__post_request(r)


if __name__ == "__main__":
    print(IPAPICom().resolve("1.1.1.1"))