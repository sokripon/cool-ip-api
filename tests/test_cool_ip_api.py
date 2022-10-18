from cool_ip_api import __version__


# TODO: Add tests for async functions
# TODO: Add tests for ratelimiting
# TODO: Add tests for error handling

def current_ip_v4():
    import httpx
    ip = httpx.get("https://api4.ipify.org").text
    return ip


def current_ip_v6():
    import httpx
    ip = httpx.get("https://api6.ipify.org").text
    return ip


def get_secret(name: str):
    with open("secrets.json") as f:
        import json
        data = json.load(f)
        return data.get(name, None)


def test_version():
    assert __version__ == '0.1.0'


class TestAbstractApiCOM:
    def setup(self):
        from cool_ip_api.provider.abstractapi_com import AbstractApiCom
        self.abstract_api = AbstractApiCom(get_secret("AbstractApiCom"))
        self.own_ip = current_ip_v4()

    def test_cloudflare(self):
        query = "1.1.1.1"
        response = self.abstract_api.resolve(query)
        assert response.ip_address == query

    def test_ownip(self):
        query = self.own_ip
        response = self.abstract_api.resolve(query)
        assert response.ip_address == query


class TestIpApiCOM:
    def setup(self):
        from cool_ip_api.provider.ip_api_com import IPAPICom
        self.ip_api_com = IPAPICom()
        self.own_ip = current_ip_v4()

    def test_cloudflare(self):
        query = "1.1.1.1"
        response = self.ip_api_com.resolve(query)
        assert response.status == "success"
        assert response.query == query
        assert response.asname == "CLOUDFLARENET"

    def test_ownip(self):
        query = self.own_ip
        response = self.ip_api_com.resolve(query)
        assert response.status == "success"
        assert response.query == query


class TestIpWhoIsIO:
    def setup(self):
        from cool_ip_api.provider.ip_who_is_io import IPWhoIsIo
        self.ipwhois_com = IPWhoIsIo()
        self.own_ip = current_ip_v4()

    def test_cloudflare(self):
        query = "1.1.1.1"
        response = self.ipwhois_com.resolve(query)
        assert response.success is True
        assert response.ip == query

    def test_ownip(self):
        query = self.own_ip
        response = self.ipwhois_com.resolve(query)
        assert response.success is True
        assert response.ip == query


class TestIpApiCO:
    def setup(self):
        from cool_ip_api.provider.ipapi_co import IPApiCO
        self.api_co = IPApiCO()
        self.own_ip = current_ip_v4()

    def test_cloudflare(self):
        query = "1.1.1.1"
        response = self.api_co.resolve(query)
        assert response.ip == query
        assert response.asn == "AS13335"

    def test_ownip(self):
        query = self.own_ip
        response = self.api_co.resolve(query)
        assert response.ip == query


class TestAPIIPApiCOM:
    def setup(self):
        from cool_ip_api.provider.ipapi_com import APIIPApiCOM
        self.api_co = APIIPApiCOM(get_secret("APIIPApiCOM"))
        self.own_ip = current_ip_v4()

    def test_cloudflare(self):
        query = "1.1.1.1"
        response = self.api_co.resolve(query)
        assert response.ip == query

    def test_ownip(self):
        query = self.own_ip
        response = self.api_co.resolve(query)
        assert response.ip == query


class TestIpifyORG:
    def setup(self):
        from cool_ip_api.provider.ipify_org import IpifyOrg
        self.api_co = IpifyOrg()
        self.own_ip_v4 = current_ip_v4()
        self.own_ip_v6 = current_ip_v6()

    def test_ipv4(self):
        response = self.api_co.resolve("ipv4")
        assert response.ipv4 == self.own_ip_v4

    def test_ipv6(self):
        response = self.api_co.resolve("ipv6")
        assert response.ipv6 == self.own_ip_v6

    def test_combined(self):
        response = self.api_co.resolve("combined")
        assert response.ipv4 == self.own_ip_v4
        assert response.ipv6 == self.own_ip_v6

    def test_dualstack(self):
        response = self.api_co.resolve("dualstack")
        assert any([response.ipv4 == self.own_ip_v4, response.ipv6 == self.own_ip_v6])


class TestIpInfoIO:
    def setup(self):
        from cool_ip_api.provider.ipinfo_io import IPInfoIo
        self.api_co = IPInfoIo(get_secret("IPInfoIo"))
        self.own_ip = current_ip_v4()

    def test_cloudflare(self):
        query = "1.1.1.1"
        response = self.api_co.resolve(query)
        assert response.ip == query
        assert response.org == "AS13335 Cloudflare, Inc."

    def test_ownip(self):
        query = self.own_ip
        response = self.api_co.resolve(query)
        assert response.ip == query


class TestMyIpWTF:
    def setup(self):
        from cool_ip_api.provider.myip_wtf import MyIpWTF
        self.api_co = MyIpWTF()
        self.own_ip_v4 = current_ip_v4()
        self.own_ip_v6 = current_ip_v6()

    def test_ipv4(self):
        response = self.api_co.resolve("ipv4")
        assert response.YourFuckingIPv4Address == self.own_ip_v4

    def test_ipv6(self):
        response = self.api_co.resolve("ipv6")
        assert response.YourFuckingIPv6Address == self.own_ip_v6

    def test_combined(self):
        response = self.api_co.resolve("combined")
        assert response.YourFuckingIPv4Address == self.own_ip_v4
        assert response.YourFuckingIPv6Address == self.own_ip_v6

    def test_dualstack(self):
        response = self.api_co.resolve("dualstack")
        assert any(
            [response.YourFuckingIPv4Address == self.own_ip_v4, response.YourFuckingIPv6Address == self.own_ip_v6])
