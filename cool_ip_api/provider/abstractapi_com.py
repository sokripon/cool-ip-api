from __future__ import annotations
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional

import httpx
from pydantic import BaseModel

from cool_ip_api.provider.resolver_abc import ResolverFull, valid_ip_types
from cool_ip_api.utils.errors import RateLimitError, QuotaError


class Security(BaseModel):
    is_vpn: Optional[bool]


class Timezone(BaseModel):
    name: Optional[str]
    abbreviation: Optional[str]
    gmt_offset: Optional[int] | str
    current_time: Optional[str]
    is_dst: Optional[bool] | str


class Flag(BaseModel):
    emoji: Optional[str]
    unicode: Optional[str]
    png: Optional[str]
    svg: Optional[str]


class Currency(BaseModel):
    currency_name: Optional[str]
    currency_code: Optional[str]


class Connection(BaseModel):
    autonomous_system_number: Optional[int]
    autonomous_system_organization: Optional[str]
    connection_type: Optional[str]
    isp_name: Optional[str]
    organization_name: Optional[str]


class AbstractApiComResponse(BaseModel):
    ip_address: Optional[str]
    city: Optional[str]
    city_geoname_id: Optional[int]
    region: Optional[str]
    region_iso_code: Optional[str]
    region_geoname_id: Optional[int]
    postal_code: Optional[str]
    country: Optional[str]
    country_code: Optional[str]
    country_geoname_id: Optional[int]
    country_is_eu: Optional[bool]
    continent: Optional[str]
    continent_code: Optional[str]
    continent_geoname_id: Optional[int]
    longitude: Optional[float]
    latitude: Optional[float]
    security: Security
    timezone: Timezone
    flag: Optional[Flag]
    currency: Optional[Currency]
    connection: Connection


class AbstractApiCom(ResolverFull):
    """
    | Resolver for IP addresses.
    | Website: https://www.abstractapi.com/api/ip-geolocation-api
    | Limit is 20000 requests per month (api key based check)
    | Limit 1 request per second
    | No commercial use allowed see https://www.abstractapi.com/api/ip-geolocation-api
    """
    # TODO: Premium API support

    base_url = "https://ipgeolocation.abstractapi.com/v1/"
    _request_limit_amount = 1
    _request_limit_time_period_seconds = 1

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.requests_left = self._request_limit_amount
        self.reset_time = datetime.now() + timedelta(seconds=self._request_limit_time_period_seconds)

    def __pre_request(self):
        if self.reset_time < datetime.now():
            self.reset_time = datetime.now() + timedelta(seconds=self._request_limit_time_period_seconds)
            self.requests_left = self._request_limit_amount
        if self.requests_left <= 0:
            raise RateLimitError("You have reached the request limit for this API")

    def resolve(self, ip: valid_ip_types = "", httpx_args: Optional[dict] = None) -> AbstractApiComResponse:
        """
        | Resolves an IP address.
        :param ip: The IP address to resolve. If not provided, the IP address of the client is used.
        :param httpx_args: Arguments to pass to httpx.get()
        :return: API Response as a pydantic model
        :rtype: AbstractApiComResponse
        """
        self.__pre_request()
        url = f"{self.base_url}?api_key={self.api_key}{f'&ip_address={ip}' if ip else ''}"
        print(url)

        r = httpx.get(url, **httpx_args or {})
        return self.__post_request(r)

    def __post_request(self, r: httpx.Response):
        if r.status_code in [200, 204]:
            self.requests_left -= 1
            return AbstractApiComResponse(**r.json())
        elif r.status_code == 429:
            self.reset_time = datetime.now() + timedelta(seconds=self._request_limit_time_period_seconds)
            self.requests_left = 0
            raise RateLimitError("You sent requests too fast")
        elif r.status_code == 422:
            self.requests_left = 0
            self.reset_time = datetime.now() + timedelta(days=30)
            raise QuotaError("You have reached the request limit for this API")

    async def async_resolve(self, ip: valid_ip_types = "", httpx_args: Optional[dict] = None) -> AbstractApiComResponse:
        """
        | Resolves an IP address.
        :param ip: The IP address to resolve. If not provided, the IP address of the client is used.
        :param httpx_args: Arguments to pass to httpx.get()
        :return: API Response as a pydantic model
        :rtype: AbstractApiComResponse
        """
        self.__pre_request()
        url = f"{self.base_url}?api_key={self.api_key}{f'&ip_address={ip}' if ip else ''}"

        async with httpx.AsyncClient() as client:
            r = await client.get(url, **httpx_args or {})
            return self.__post_request(r)
