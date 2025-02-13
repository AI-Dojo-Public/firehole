import sys
import yaml
import socket
from multiprocessing import Process

from firehole.proxies import Proxy


def create_and_start_proxy(description: dict):
    if description["host"] == "auto":
        description["host"] = socket.gethostbyname(socket.gethostname())
    Proxy[description["type"]].value.create(**description).start()


def start(configuration: dict) -> None:
    """
    Create and start the proxies using the provided configuration.
    :param configuration: Application configuration
    :return: None
    """
    processes: list[Process] = list()
    for application in configuration["applications"]:
        process = Process(target=create_and_start_proxy, args=(application,))
        processes.append(process)

    # If there is an error in the configuration, start only if all the proxies are created successfully
    for process in processes:
        process.start()

    try:
        for process in processes:
            process.join()
    except KeyboardInterrupt:
        for process in processes:
            process.kill()


def load_configuration(configuration_path: str) -> dict:
    """
    Load application configuration from file.
    :param configuration_path: Path to the configuration file
    :return: Application configuration
    """
    with open(configuration_path) as config_file:
        return yaml.safe_load(config_file)


def cli() -> None:
    """
    Application entrypoint.
    :return: None
    """
    if len(sys.argv) != 2:
        print("Usage: firehole /path/to/config.yml")
        sys.exit(1)

    configuration = load_configuration(sys.argv[1])
    start(configuration)
