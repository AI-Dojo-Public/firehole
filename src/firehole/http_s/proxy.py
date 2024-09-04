from http.server import SimpleHTTPRequestHandler, HTTPServer
import ssl
import requests
from importlib import import_module

from firehole.utility.logger import logger
from firehole.http_s.vulnerabilities.abstract import VulnerabilityAbstract


class ProxyHandler(SimpleHTTPRequestHandler):
    server: "ProxyServer"

    def log_request_details(self):
        logger.info(f"Request Method: {self.command}")
        logger.info(f"Request Path: {self.path}")
        logger.info(f"Request Headers: {self.headers}")

        content_length = int(self.headers.get('Content-Length', 0))
        if content_length > 0:
            request_body = self.rfile.read(content_length)
            logger.info(f"Request Body: {request_body.decode('utf-8', 'ignore')}")
        else:
            logger.info("No Request Body")

    def do_GET(self):
        self.log_request_details()

        for vulnerability in self.server.vulnerabilities:
            if vulnerability(self).check():
                break
        else:
            try:
                # Use Docker service name
                target_url = f"http{'s' if self.server.tls else ''}://{self.server.origin_host}:{self.server.origin_port}{self.path}"
                logger.info(f"Forwarding GET request to: {target_url}")

                # Use the cert's verify option
                response = requests.get(target_url, verify='/usr/src/app/src/firehole/http_s/cert.pem')

                logger.info(f"Response status code: {response.status_code}")
                logger.info(f"Response headers: {response.headers}")
                logger.info(f"Response content: {response.text}")

                self.send_response(response.status_code)
                for header, value in response.headers.items():
                    self.send_header(header, value)
                self.end_headers()
                self.wfile.write(response.content)
                logger.info("Forwarded response sent successfully")
            except requests.RequestException as e:
                logger.error(f"Error during request to target URL: {e}")
                self.send_response(500)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(f"Error: {e}".encode())

# # Expected type '(Any, Any, HTTPServer) -> BaseRequestHandler' (matched generic type '(Any, Any, Self) -> BaseRequestHandler')
# def asd(a, b, c):
#     return ProxyHandler(a, b, c)


class ProxyServer(HTTPServer):
    def __init__(self, address: tuple[str, int], origin_host: str, origin_port: int, tls: bool, vulnerabilities: list[str]):
        super().__init__(address, ProxyHandler)  # This is fine, Python just doesn't understand
        self.origin_host = origin_host
        self.origin_port = origin_port
        self.tls = tls
        self.vulnerabilities: list[VulnerabilityAbstract] = list()
        for vulnerability in vulnerabilities:
            self.vulnerabilities.append(import_module(f"firehole.http_s.vulnerabilities.{vulnerability.replace('-', '_').lower()}.main").Vulnerability)


class HTTPProxy:
    def __init__(self, host: str, port: int, origin_host: str, origin_port: int, certificate: str, private_key: str, vulnerabilities: list[str]):
        self.host = host
        self.port = port
        self.context = self.get_ssl_context(certificate, private_key) if certificate and private_key else None
        tls: bool = self.context is not None
        self.httpd = ProxyServer((self.host, self.port), origin_host, origin_port, tls, vulnerabilities)

    def get_ssl_context(self, cert_file: str, key_file: str):
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(cert_file, key_file)
        context.set_ciphers("@SECLEVEL=1:ALL")

        return context

    def start(self):
        if self.context:
            self.httpd.socket = self.context.wrap_socket(self.httpd.socket, server_side=True)
        logger.info(f"Starting HTTP proxy on {self.host}:{self.port}")
        self.httpd.serve_forever()
