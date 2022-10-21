def cli():
    import argparse
    from cool_ip_api.provider.ip_api_com import IPAPICom
    from pprint import pprint
    parser = argparse.ArgumentParser(description='Get IP info')
    parser.add_argument('ip', type=str, help='IP address', default=None, nargs='?')
    args = parser.parse_args()
    ip_info_provider = IPAPICom()
    pprint(ip_info_provider.resolve(args.ip).json())


if __name__ == "__main__":
    cli()
