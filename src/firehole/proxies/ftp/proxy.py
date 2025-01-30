import socket
from typing import Self
import select

from firehole.utility.logger import logger
from firehole.abstract.proxy import ProxyAbstract
import re
import threading
from enum import StrEnum


class Method(StrEnum):
    EPSV = "EPSV"
    # PASV = "PASV"  # unimplemented


class EPSVCommunicationHandler:
    def __init__(self, host, server_address, logger_obj):
        self.data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.data_socket.bind((host, 0))
        self.data_socket_port = self.data_socket.getsockname()[1]
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = server_address
        self.logger = logger_obj.bind()

    def start(self):
        self.server_socket.connect(self.server_address)
        self.data_socket.listen(1)
        client_socket, address = self.data_socket.accept()

        while True:
            data = self.server_socket.recv(8196)
            self.logger.info("data", data=data)
            if not data:
                client_socket.close()
                self.data_socket.close()
                self.server_socket.close()
                return
            client_socket.sendall(data)


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
        # Initial hello from server
        self.server_socket.connect((self.origin_host, self.origin_port))
        server_data = self.server_socket.recv(8192)
        self.client_socket.sendall(server_data)
        extended_mode: Method | None = None

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
                    match extended_mode:
                        case Method.EPSV:
                            decoded = data.decode()
                            match = re.search(r"\|\|\|(\d+)\|", decoded)
                            if match:
                                port = int(match.group(1))
                                c = EPSVCommunicationHandler(self.host, (self.origin_host, port), self.logger)
                                threading.Thread(target=c.start).start()
                                decoded = re.sub(r"\|\|\|(\d+)\|", f"|||{c.data_socket_port}|", decoded)
                                data = decoded.encode()
                                self.logger.info("epsv", data=data)
                        case _:
                            pass
                    self.client_socket.sendall(data)
                else:
                    data = sock.recv(8192)
                    self.logger.info("client data", data=data)
                    [vulnerability(data, self.logger).check_and_exploit() for vulnerability in self._vulnerabilities]
                    if not data:
                        self.clean_up()
                        return

                    decoded = data.decode()
                    for method in Method:
                        if decoded.startswith(method):
                            extended_mode = method
                    self.server_socket.sendall(data)

    def clean_up(self):
        self.client_socket.close()
        self.server_socket.close()


class ProxyFTP(ProxyAbstract):
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
        self.logger.info("FTP Proxy is running")

        while True:
            client_socket, address = self.socket.accept()
            self.logger.info("New client connection", source=address)
            self.start_client_handler(client_socket)

    def start_client_handler(self, client_socket):
        handler = CommunicationHandler(
            self.origin_host, self.origin_port, client_socket, self.logger, self.host, self._vulnerabilities
        )
        threading.Thread(target=handler.start).start()
