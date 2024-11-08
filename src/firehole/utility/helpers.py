from importlib import import_module
from typing import Type

from firehole.abstract.vulnerability import VulnerabilityAbstract


def import_vulnerability(proxy_module: str, vulnerability_name: str) -> Type[VulnerabilityAbstract]:
    """
    Import a vulnerability of the selected proxy module.
    :param proxy_module: Name of the proxy - its root Python package it resides in (e.g. `http_`)
    :param vulnerability_name: Vulnerability name - its root Python package it resides in (e.g. `CVE-1-2`)
    :return: Vulnerability class
    """
    parsed_vulnerability = vulnerability_name.replace("-", "_").lower()
    return import_module(f"firehole.proxies.{proxy_module}.vulnerabilities.{parsed_vulnerability}.main").Vulnerability
