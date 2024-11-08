from enum import Enum, EnumMeta

from firehole.proxies.http_.proxy import ProxyHTTP


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


__all__ = [
    "Proxy",
    "ProxyHTTP",
]
