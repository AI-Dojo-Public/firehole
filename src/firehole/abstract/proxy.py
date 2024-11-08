from abc import ABC, abstractmethod


class ProxyAbstract(ABC):
    @abstractmethod
    def start(self) -> None:
        """
        Start the proxy.
        :return: None
        """

    @staticmethod
    @abstractmethod
    def create(**kwargs) -> "ProxyAbstract":
        """
        Create a proxy instance.
        :param kwargs: Arguments used for the proxy creation
        :return: Instance of the proxy
        """
