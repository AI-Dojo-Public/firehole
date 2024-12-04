import time
from typing import Self

from firehole.utility.logger import logger
from firehole.abstract.proxy import ProxyAbstract


# TODO: Update the name of the proxy package/directory
class ProxyNew(ProxyAbstract):  # TODO: Update the class name
    def __init__(self, host: str, port: int, vulnerabilities: list[str]):
        """
        Example proxy
        :param host: Desired host
        :param port: Desired port
        :param vulnerabilities: Allowed vulnerabilities
        """
        self._logger = logger.bind(host=host, port=port)
        self._vulnerability_names = vulnerabilities
        self._vulnerabilities = [self.import_vulnerability(vulnerability) for vulnerability in vulnerabilities]

    @classmethod
    def create(cls, **kwargs) -> Self:
        """
        Parse the config and instantiate the proxy.
        :param kwargs: Raw arguments from the config
        :return: Proxy instance
        """
        return cls(kwargs["host"], kwargs["port"], kwargs.get("vulnerabilities", []))

    def start(self) -> None:
        """
        Start and run the proxy forever.
        :return: None
        """
        self._logger.info(f"Starting my proxy", vulnerabilities=self._vulnerability_names)
        # Do stuff
        while True:
            if self._vulnerabilities[0](self._logger).check_and_exploit():
                break
            time.sleep(0.3)
