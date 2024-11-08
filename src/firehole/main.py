import sys
import yaml

from firehole.proxies import Proxy
from multiprocessing import Process


def start(configuration: dict) -> None:
    """
    Create and start the proxies using the provided configuration.
    :param configuration: Application configuration
    :return: None
    """
    processes: list[Process] = list()
    for application in configuration["applications"]:
        proxy = Proxy[application["type"]].value.create(**application)
        process = Process(target=proxy.start)
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
