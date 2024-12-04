from http.server import SimpleHTTPRequestHandler, HTTPServer
import ssl
import requests
from requests.structures import CaseInsensitiveDict
from uuid import uuid1
from typing import Self

from firehole.utility.logger import logger
from firehole.abstract.proxy import ProxyAbstract


class RequestHandler(SimpleHTTPRequestHandler):
    server: "ProxyHTTP"

    def __init__(self, request, client_address, server: "ProxyHTTP"):
        """
        RequestHandler is created for each request.
        The __init__ method calls the `do_` methods accordingly.
        :param request: HTTP request
        :param client_address: Host and port of the client
        :param server: The server that created this RequestHandler
        """
        self.logger = server.logger.bind(request_uuid=str(uuid1()))
        super().__init__(request, client_address, server)

    def do_GET(self) -> None:
        """
        Process the GET request.
        :return: None
        """
        self.logger.info("handling GET request", method=self.command, path=self.path, headers=self.headers)
        for vulnerability in self.server.vulnerabilities:
            if vulnerability(self).check_and_exploit():
                return

        self._forward_request()

    def _forward_request(self) -> None:
        """
        Forward the request to the real server and send its response.
        :return: None
        """
        target_url = f"{self.server.origin_url}{self.path}"
        self.logger.debug("Forwarding request", target_url=target_url)
        try:
            response = requests.get(target_url, verify=self.server.certificate)
            code, headers, content = response.status_code, response.headers, response.content
        except requests.RequestException as ex:
            code, headers, content = 500, CaseInsensitiveDict({"Content-type": "text/plain"}), b"Internal server error"
            self.logger.warning("Error during request to origin", error=str(ex))

        self.send_full_response(code, headers, content)

    def send_full_response(self, status_code: int, headers: CaseInsensitiveDict, content: bytes) -> None:
        """
        Send response to the original request.
        :param status_code: Response status code
        :param headers: Response headers
        :param content: Response content
        :return: None
        """
        self.logger.debug("Sending response")
        self.send_response(status_code)
        for header, value in headers.items():
            self.send_header(header, value)
        self.end_headers()
        self.wfile.write(content)
        self.logger.info("Response sent", status_code=status_code, headers=headers, content=content)


class ProxyHTTP(ProxyAbstract, HTTPServer):
    def __init__(
        self,
        host: str,
        port: int,
        origin_host: str,
        origin_port: int,
        certificate: str | None,
        private_key: str | None,
        vulnerabilities: list[str],
    ):
        """
        Proxy used for intercepting HTTP traffic.
        :param host: Desired host
        :param port: Desired port
        :param origin_host: Host to redirect the traffic to
        :param origin_port: Port to redirect the traffic to
        :param certificate: Certificate used for TLS
        :param private_key: Private key used for TLS
        :param vulnerabilities: Allowed vulnerabilities
        """
        self._logger = logger.bind(host=host, port=port)
        self._certificate = certificate
        self._private_key = private_key
        self._vulnerability_names = vulnerabilities
        self._vulnerabilities = [self.import_vulnerability(vulnerability) for vulnerability in vulnerabilities]
        self._context = self.create_ssl_context(certificate, private_key) if certificate and private_key else None
        self._origin_url = f"http{'s' if self._context else ''}://{origin_host}:{origin_port}"
        super().__init__((host, port), RequestHandler)

    @property
    def origin_url(self):
        return self._origin_url

    @property
    def vulnerabilities(self):
        return self._vulnerabilities

    @property
    def certificate(self):
        return self._certificate

    @property
    def logger(self):
        return self._logger

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
            kwargs.get("certificate"),
            kwargs.get("private_key"),
            kwargs.get("vulnerabilities", []),
        )

    def start(self) -> None:
        """
        Start and run the proxy forever.
        :return: None
        """
        self.logger.info(
            f"Starting HTTP proxy",
            vulnerabilities=self._vulnerability_names,
            origin_address=self.origin_url,
            certificate=self.certificate,
            private_key=self._private_key,
        )
        if self._context:
            self.socket = self._context.wrap_socket(self.socket, server_side=True)
        self.serve_forever()

    @staticmethod
    def create_ssl_context(cert_file_path: str, key_file_path: str) -> ssl.SSLContext:
        """
        Create SSL context.
        :param cert_file_path: Path to the certificate file
        :param key_file_path: Path to the private key file
        :return: SSL Context
        """
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(cert_file_path, key_file_path)
        context.set_ciphers("@SECLEVEL=1:ALL")

        return context
