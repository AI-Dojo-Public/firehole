from abc import ABC, abstractmethod
from typing import Self, Type
from importlib import import_module

from firehole.abstract.vulnerability import VulnerabilityAbstract


class ProxyAbstract(ABC):
    @abstractmethod
    def start(self) -> None:
        """
        Start the proxy.
        :return: None
        """

    @classmethod
    @abstractmethod
    def create(cls, **kwargs) -> Self:
        """
        Create a proxy instance.
        :param kwargs: Arguments used for the proxy creation
        :return: Instance of the proxy
        """

    def import_vulnerability(self, vulnerability_name: str) -> Type[VulnerabilityAbstract]:
        """
        Import a vulnerability of the selected proxy module.
        :param vulnerability_name: Vulnerability name - its root Python package it resides in (e.g. `CVE-1-2`)
        :return: Vulnerability class
        """
        proxy_name = self.__module__.rsplit(".")[2]
        parsed_vulnerability = vulnerability_name.replace("-", "_").lower()
        return import_module(f"firehole.proxies.{proxy_name}.vulnerabilities.{parsed_vulnerability}.main").Vulnerability
