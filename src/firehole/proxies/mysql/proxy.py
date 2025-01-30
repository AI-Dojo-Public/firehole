import socket
import threading
import select
from typing import Self, cast

from firehole.abstract.proxy import ProxyAbstract
from firehole.utility.logger import logger
from firehole.proxies.mysql.vulnerabilities.vulnerability import MySQLVulnerabilityAbstract


class ProxyMySQL(ProxyAbstract):
    def __init__(
        self,
        host: str,
        port: int,
        origin_host: str,
        origin_port: int,
        vulnerabilities: list[str],
    ):
        """
        Proxy used for intercepting MySQL traffic.
        :param host: Desired host (proxy's host)
        :param port: Desired port (proxy's port)
        :param origin_host: Host to redirect the traffic to (MySQL server)
        :param origin_port: Port to redirect the traffic to (MySQL server port)
        """
        self._host = host
        self._port = port
        self._origin_host = origin_host
        self._origin_port = origin_port
        self._vulnerability_names = vulnerabilities
        self._vulnerabilities = [self.import_vulnerability(vulnerability) for vulnerability in vulnerabilities]
        self._logger = logger.bind(host=host, port=port)

    @classmethod
    def create(cls, **kwargs) -> Self:
        """
        Parse the config and instantiate the proxy.
        :param kwargs: Raw arguments from the config
        :return: Proxy instance
        """
        return cls(
            kwargs["host"],
            kwargs["port"],
            kwargs["origin_host"],
            kwargs["origin_port"],
            kwargs.get("vulnerabilities", []),
        )

    def handle_client(self, client_socket: socket.socket):
        """
        Handles the communication between the client and the MySQL server.
        """
        # Instantiate vulnerabilities
        vulnerabilities: list[MySQLVulnerabilityAbstract] = list()
        for vulnerability in self._vulnerabilities:
            vulnerabilities.append(cast(MySQLVulnerabilityAbstract, vulnerability(self._logger)))

        # Initialize the communication with the server
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.connect((self._origin_host, self._origin_port))
        self._logger.debug("Connected to MySQL server.")

        # Start proxying the client/server communication
        exit_flag = False
        while not exit_flag:
            read_sockets, _, _ = select.select([server_socket, client_socket], [], [])
            for sock in read_sockets:
                if sock == server_socket:
                    data = server_socket.recv(4096)
                    self._logger.info("server data", data=data)
                    if not data:
                        exit_flag = True
                        break
                    [vulnerability.check_and_exploit(data) for vulnerability in vulnerabilities]
                    client_socket.sendall(data)

                else:
                    data = client_socket.recv(4096)
                    self._logger.info("client data", data=data)
                    if not data:
                        exit_flag = True
                        break
                    for vulnerability in vulnerabilities:
                        if vulnerability.check_and_exploit(data) and (modified_data := vulnerability.data) is not None:
                            data = modified_data
                    server_socket.sendall(data)

        client_socket.close()
        server_socket.close()

    def start(self) -> None:
        """
        Starts the proxy server and handles incoming connections.
        """
        self._logger.info("Starting MySQL Proxy", origin=(self._origin_host, self._origin_port))
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self._host, self._port))
        server_socket.listen(5)

        while True:
            client_socket, address = server_socket.accept()
            self._logger.debug("New client connected.", address=address)
            client_handler = threading.Thread(target=self.handle_client, args=(client_socket,))
            client_handler.start()
