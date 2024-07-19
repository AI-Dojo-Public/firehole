from http.server import SimpleHTTPRequestHandler, HTTPServer
import ssl
import os
import requests
from enum import Enum


def get_ssl_context(certfile, keyfile):
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile, keyfile)
    context.set_ciphers("@SECLEVEL=1:ALL")
    return context


class ProxyHandler(SimpleHTTPRequestHandler):
    # def do_POST(self):
    #     content_length = int(self.headers["Content-Length"])
    #     post_data = self.rfile.read(content_length)
    #     print(post_data.decode("utf-8"))

    def do_GET(self):
        current_path = os.path.dirname(os.path.realpath(__file__))
        r = requests.get(f"https://localhost:4434{self.path}", verify=f"{current_path}/cert.pem")

        self.send_response(r.status_code)
        for k, v in r.headers.items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(r.content)


class TestHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        response = b"asd"
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Content-length', str(len(response)))
        self.end_headers()
        self.wfile.write(response)


class Handler(Enum):
    PROXY = ProxyHandler
    TEST = TestHandler


def run_server(address: str, port: int, handler: Handler):
    current_path = os.path.dirname(os.path.realpath(__file__))
    context = get_ssl_context(f"{current_path}/cert.pem", f"{current_path}/key.pem")

    httpd = HTTPServer((address, port), handler.value)
    httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
    httpd.serve_forever()
