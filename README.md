# cool-ip-api

<a href="https://pypi.org/project/cool-ip-api/">
    <img src="https://badge.fury.io/py/cool-ip-api.svg" alt="Package version">
</a>

A package to get information from multiple IP APIs about the clients IP or another requested IP.<br>

## Installation
**Requires python  3.10 and above.**
```bash
pip install cool-ip-api
```

## Usage

```python
# Example with IPApiCom API
from cool_ip_api.provider.ip_api_com import IPAPICom

ip_api_com = IPAPICom()
ip_api_com.resolve() # Returns a pydantic model with the data from the API
```

### Cli command

```bash
cool-ip-api
cool-ip-api 1.1.1.1
```

## Supported APIs

| Provider                                                              | Free plan available?                  | Rate limit   | Check   | IP Query |
|-----------------------------------------------------------------------|---------------------------------------|--------------|---------|----------|
| [abstractapi.com](https://www.abstractapi.com/api/ip-geolocation-api) | ✅                                     | 20.000/month | api-key | ✅        |
| [ip-api.com](https://ip-api.com/)                                     | ✅                                     | 45/minute    | ip      | ✅        |
| [ipwhois.io](https://ipwhois.io/)                                     | ✅                                     | 10.000/month | ip      | ✅        |
| [ipapi.co](https://ipapi.co/)                                         | ✅                                     | 1.000/day    | ip      | ✅        |
| [ipapi.com](https://ipapi.com/)                                       | ✅                                     | 1.000/month  | api-key | ✅        |
| [ipify.org](https://www.ipify.org/)                                   | ✅                                     | None         | None    | ❌        |
| [ipinfo.io](https://ipinfo.io/)                                       | ✅                                     | 50.000/month | api-key | ✅        |
| [myip.wtf](https://myip.wtf/)                                         | ✅ ([Donate](https://myip.wtf/donate)) | 1/minute     | ip      | ❌        |

## TODO

- [ ] Add more providers
    - [ ] [geo.ipify.org](https://geo.ipify.org/)
- [ ] Add bulk query support for providers that support it
- [ ] Add premium plan support for providers that support it
- [ ] Add more tests
    - [ ] Async tests
    - [ ] Rate limit tests
- [ ] Add more documentation