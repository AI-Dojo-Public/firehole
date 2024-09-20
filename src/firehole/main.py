import sys
import yaml

from firehole.http_s.proxy import HTTPProxy
from firehole.utility.helpers import ProxyProcess


def main():
    if len(sys.argv) != 2:
        print("Usage: firehole /path/to/config.yml")
        sys.exit(1)

    config_path = sys.argv[1]
    with open(config_path) as config_file:
        configuration = yaml.safe_load(config_file)

    proxies: list[ProxyProcess] = list()
    for application in configuration["applications"]:
        match application["type"]:
            case "http_s":
                proxy = HTTPProxy(
                    application["host"],
                    application["port"],
                    application["origin_host"],
                    application["origin_port"],
                    application.get("certificate"),
                    application.get("private_key"),
                    application.get("vulnerabilities", [])
                )
                process = ProxyProcess(proxy)
                proxies.append(process)
                process.start()
            case _:
                print(f"Unknown proxy type {application['type']}")
