import socket
from typing import Self
import select

from firehole.utility.logger import logger
from firehole.abstract.proxy import ProxyAbstract
import threading


class CommunicationHandler:
    def __init__(
        self, origin_host: str, origin_port: int, client_socket: socket.socket, logger_obj, host, vulnerabilities
    ):
        self.host = host
        self.origin_host = origin_host
        self.origin_port = origin_port
        self.client_socket = client_socket
        self.logger = logger_obj.bind()
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.data_socket = None
        self._vulnerabilities = vulnerabilities

    def start(self):
        self.server_socket.connect((self.origin_host, self.origin_port))
        while True:
            read_sockets, _, _ = select.select([self.server_socket, self.client_socket], [], [])
            for sock in read_sockets:
                sock: socket.socket
                if sock == self.server_socket:
                    data = sock.recv(8192)
                    self.logger.info("server data", data=data)
                    [vulnerability(data, self.logger).check_and_exploit() for vulnerability in self._vulnerabilities]
                    if not data:
                        self.clean_up()
                        return
                    self.client_socket.sendall(data)
                else:
                    data = sock.recv(8192)
                    self.logger.info("client data", data=data)
                    [vulnerability(data, self.logger).check_and_exploit() for vulnerability in self._vulnerabilities]
                    if not data:
                        self.clean_up()
                        return
                    self.server_socket.sendall(data)

    def clean_up(self):
        self.client_socket.close()
        self.server_socket.close()


class ProxySMB(ProxyAbstract):
    def __init__(self, host: str, port: int, origin_host: str, origin_port: int, vulnerabilities: list[str]):
        self._logger = logger.bind(host=host, port=port)
        self.host = host
        self.port = port
        self.origin_host = origin_host
        self.origin_port = origin_port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._vulnerabilities = [self.import_vulnerability(vulnerability) for vulnerability in vulnerabilities]

    @property
    def logger(self):
        return self._logger

    @classmethod
    def create(cls, **kwargs) -> Self:
        return cls(
            kwargs["host"],
            kwargs["port"],
            kwargs["origin_host"],
            kwargs["origin_port"],
            kwargs.get("vulnerabilities", []),
        )

    def start(self):
        self.socket.bind((self.host, self.port))
        self.socket.listen(5)
        self.logger.info("SMB Proxy is running")

        while True:
            client_socket, address = self.socket.accept()
            self.logger.info("New client connection", source=address)
            self.start_client_handler(client_socket)

    def start_client_handler(self, client_socket):
        handler = CommunicationHandler(
            self.origin_host, self.origin_port, client_socket, self.logger, self.host, self._vulnerabilities
        )
        threading.Thread(target=handler.start).start()
