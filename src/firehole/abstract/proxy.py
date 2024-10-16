from abc import ABC, abstractmethod


class ProxyAbstract(ABC):
    @abstractmethod
    def start(self) -> None:
        """
        Start the proxy.
        :return: None
        """
