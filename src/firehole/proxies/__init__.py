from enum import Enum, EnumMeta

from firehole.proxies.http_.proxy import ProxyHTTP
from firehole.proxies.ftp.proxy import ProxyFTP
from firehole.proxies.mysql.proxy import ProxyMySQL


class ProxyMeta(EnumMeta):
    """
    Overrides base metaclass of Enum in order to support custom exception when accessing not present item.
    """

    def __getitem__(self, item):
        try:
            return super().__getitem__(item)
        except KeyError:
            raise KeyError(f"{item} proxy is not supported. Supported types: {', '.join([i.name for i in list(self)])}")


class Proxy(Enum, metaclass=ProxyMeta):
    http = ProxyHTTP
    ftp = ProxyFTP
    mysql = ProxyMySQL


__all__ = [
    "Proxy",
    "ProxyHTTP",
    "ProxyFTP",
    "ProxyMySQL",
]
