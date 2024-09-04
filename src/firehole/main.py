import sys
import yaml
from firehole.http_s.proxy import HTTPProxy


def main():
    if len(sys.argv) != 2:
        print("Usage: firehole /path/to/config.yml")
        sys.exit(1)

    config = sys.argv[1]
    with open(config) as config_file:
        configuration = yaml.safe_load(config_file)

    for application in configuration["applications"]:
        if application["type"] == "http_s":
            HTTPProxy(
                application["host"],
                application["port"],
                application["origin_host"],
                application["origin_port"],
                application.get("certificate"),
                application.get("private_key"),
                application.get("vulnerabilities", [])
            ).start()
        else:
            print(f"Unknown proxy type {application['type']}")
