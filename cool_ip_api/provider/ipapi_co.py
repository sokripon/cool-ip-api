from __future__ import annotations
from __future__ import annotations
from __future__ import annotations

from datetime import datetime, timedelta
from enum import Enum
from typing import Optional

import httpx
from pydantic import BaseModel

from cool_ip_api.provider.resolver_abc import ResolverFull, valid_ip_types
from cool_ip_api.utils.errors import RateLimitError, AuthenticationError, ApiException, InvalidInputError


class Version(Enum):
    IPV6 = "IPv6"
    IPV4 = "IPv4"


class IPApiCOResponse(BaseModel):
    ip: str
    network: str
    version: Version
    city: str
    region: str
    region_code: str
    country: str
    country_name: str
    country_code: str
    country_code_iso3: str
    country_capital: str
    country_tld: str
    continent_code: str
    in_eu: bool
    postal: str
    latitude: float
    longitude: float
    timezone: str
    utc_offset: str
    country_calling_code: str
    currency: str
    currency_name: str
    languages: str
    country_area: float
    country_population: int
    asn: str
    org: str


class IPApiCO(ResolverFull):
    """
    | Resolver for IP addresses.
    | Website: https://ipapi.co/
    | Limit is 1000 requests per day (ip based check)
    | Commercial seems allowed? https://ipapi.co/pricing/
    """
    # TODO: Premium API support

    base_url = "https://ipapi.co/"
    _request_limit_amount = 1000
    _request_limit_time_period_seconds = 60 * 60 * 24

    def __init__(self):
        self.requests_left = self._request_limit_amount
        self.reset_time = datetime.now() + timedelta(seconds=self._request_limit_time_period_seconds)

    def __pre_request(self):
        if self.reset_time < datetime.now():
            self.reset_time = datetime.now() + timedelta(seconds=self._request_limit_time_period_seconds)
            self.requests_left = self._request_limit_amount
        if self.requests_left <= 0:
            raise RateLimitError("You have reached the request limit for this API")

    def resolve(self, ip: valid_ip_types = "", httpx_args: Optional[dict] = None) -> IPApiCOResponse:
        """
        | Resolves an IP address.
        :param ip: The IP address to resolve. If not provided, the IP address of the client is used.
        :param httpx_args: Arguments to pass to httpx.get()
        :return: API Response as a pydantic model
        :rtype: IPApiCOResponse
        """
        ip = ip or ""
        self.__pre_request()
        url = f"{self.base_url}{str(ip) + '/' if ip else ''}json/"

        r = httpx.get(url, **httpx_args or {})
        return self.__post_request(r)

    def __post_request(self, r: httpx.Response):
        if r.status_code == 200:
            self.requests_left -= 1
            return IPApiCOResponse(**r.json())
        elif r.status_code == 429:
            self.reset_time = datetime.now() + timedelta(seconds=self._request_limit_time_period_seconds)
            self.requests_left = 0
            raise RateLimitError("You sent too many requests")
        elif r.status_code == 403:
            raise AuthenticationError("Invalid API key")
        elif r.status_code == 405:
            raise InvalidInputError("Method not allowed")
        elif r.status_code == 404:
            raise InvalidInputError("Not found")
        elif r.status_code == 400:
            raise InvalidInputError("Bad request")
        raise ApiException(f"Unknown error: {r.status_code} {r.text}")

    async def async_resolve(self, ip: valid_ip_types = "", httpx_args: Optional[dict] = None) -> IPApiCOResponse:
        """
        | Resolves an IP address.
        :param ip: The IP address to resolve. If not provided, the IP address of the client is used.
        :param httpx_args: Arguments to pass to httpx.get()
        :return: API Response as a pydantic model
        :rtype: IPApiCOResponse
        """
        ip = ip or ""
        self.__pre_request()
        url = f"{self.base_url}{str(ip) + '/' if ip else ''}json/"

        async with httpx.AsyncClient() as client:
            r = await client.get(url, **httpx_args or {})
            return self.__post_request(r)
