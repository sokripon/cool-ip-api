from __future__ import annotations
from __future__ import annotations
from __future__ import annotations

from datetime import datetime, timedelta
from enum import Enum
from typing import List
from typing import Optional

import httpx
from pydantic import BaseModel

from cool_ip_api.provider.resolver_abc import ResolverFull, valid_ip_types
from cool_ip_api.utils.errors import RateLimitError, ApiException, AuthenticationError, QuotaError, InvalidInputError


class Language(BaseModel):
    code: str
    name: str
    native: str


class Location(BaseModel):
    geoname_id: int
    capital: str
    languages: List[Language]
    country_flag: str
    country_flag_emoji: str
    country_flag_emoji_unicode: str
    calling_code: str
    is_eu: bool


class Type(Enum):
    ipv4 = "ipv4"
    ipv6 = "ipv6"


class APIIPApiCOMResponse(BaseModel):
    ip: str
    type: Type
    continent_code: str
    continent_name: str
    country_code: str
    country_name: str
    region_code: str
    region_name: str
    city: str
    zip: str
    latitude: float
    longitude: float
    location: Location


class APIIPApiCOM(ResolverFull):
    """
    | Resolves an IP address.
    | Website: https://ipapi.com/
    | Limit is 1000 requests per month (api key based check)
    | Commercial use seems to be allowed? see https://ipapi.com/product
    """
    # TODO: Premium API support
    base_url = "http://api.ipapi.com/api/"

    _request_limit_amount = 1000
    _request_limit_time_period_seconds = 60 * 60 * 24 * 30

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

    def resolve(self, ip: valid_ip_types = "", httpx_args: Optional[dict] = None) -> APIIPApiCOMResponse:
        """
        | Resolves an IP address.
        :param ip: The IP address to resolve. If not provided, the IP address of the client is used.
        :param httpx_args: Arguments to pass to httpx.get()
        :return: API Response as a pydantic model
        :rtype: APIIPApiCOMResponse
        """
        self.__pre_request()
        url = f"{self.base_url}{ip or 'check'}?access_key={self.api_key}"
        r = httpx.get(url, **httpx_args or {})
        return self.__post_request(r)

    def __post_request(self, r: httpx.Response):
        if r.json().get("success") is False:
            error_code = r.json().get("error").get("code")
            error_info = r.json().get("error").get("info")
            if error_code == 101:
                raise AuthenticationError(error_info)
            elif error_code == 102:
                raise AuthenticationError(error_info)
            elif error_code == 103:
                raise ApiException(error_info)
            elif error_code == 104:
                self.reset_time = datetime.now() + timedelta(seconds=self._request_limit_time_period_seconds)
                self.requests_left = 0
                raise QuotaError(error_info)
            else:
                raise InvalidInputError(error_info)
        else:
            self.requests_left -= 1
            return APIIPApiCOMResponse(**r.json())

    async def async_resolve(self, ip: valid_ip_types = "", httpx_args: Optional[dict] = None) -> APIIPApiCOMResponse:
        """
        | Resolves an IP address.
        :param ip: The IP address to resolve. If not provided, the IP address of the client is used.
        :param httpx_args: Arguments to pass to httpx.get()
        :return: API Response as a pydantic model
        :rtype: APIIPApiCOMResponse
        """
        self.__pre_request()
        url = f"{self.base_url}{ip or 'check'}?access_key={self.api_key}"

        async with httpx.AsyncClient() as client:
            r = await client.get(url, **httpx_args or {})
            return self.__post_request(r)
