from http.server import SimpleHTTPRequestHandler, HTTPServer
import ssl
import os
import json

from firehole.utility.logger import logger


def get_ssl_context(certfile, keyfile):
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile, keyfile)
    context.set_ciphers("@SECLEVEL=1:ALL")
    return context

class TestHandler(SimpleHTTPRequestHandler):
    def log_request_details(self):
        logger.info(f"Request Method: {self.command}")
        logger.info(f"Request Path: {self.path}")
        logger.info(f"Request Headers: {self.headers}")

        # Read the request body if applicable
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length > 0:
            request_body = self.rfile.read(content_length)
            logger.info(f"Request Body: {request_body.decode('utf-8', 'ignore')}")
        else:
            logger.info("No Request Body")

    def do_GET(self):
        # Log the incoming request details
        self.log_request_details()
        
        # Extract client IP address
        client_ip = self.client_address[0]

        # Create a response with the client IP address
        response_content = {
            'client_ip': client_ip,
            'path': self.path
        }
        response_json = json.dumps(response_content, indent=4).encode('utf-8')
        
        # Send HTTP response
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Content-length', str(len(response_json)))
        self.end_headers()
        self.wfile.write(response_json)


def run_server(address: str, port: int):
    # current_path = os.path.dirname(os.path.realpath(__file__))
    # context = get_ssl_context(f"{current_path}/cert.pem", f"{current_path}/key.pem")

    httpd = HTTPServer((address, port), TestHandler)
    # httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
    logger.info(f"Starting HTTP server on {address}:{port}")
    httpd.serve_forever()


if __name__ == '__main__':
    run_server("127.0.0.1", 8000)
