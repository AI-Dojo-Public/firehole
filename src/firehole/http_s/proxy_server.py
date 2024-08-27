from http.server import SimpleHTTPRequestHandler, HTTPServer
import ssl
import os
import requests
import logging
from enum import Enum

PROXY_LOG_COLOR = '\033[94m'  # Light Blue

def get_ssl_context(certfile, keyfile):
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile, keyfile)
    context.set_ciphers("@SECLEVEL=1:ALL")
    return context

def get_vulnerable_response(host_header):
    logger.info("Returning simulated vulnerable response content from file.")
    
    base_dir = os.path.dirname(__file__)
    file_path = os.path.join(base_dir, 'vulnerable_response.html')
    
    with open(file_path, 'r') as file:
        html_content = file.read()
    
    response_content = html_content.format(host_header=host_header)
    
    return response_content

logger = logging.getLogger('proxy_server')
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter(PROXY_LOG_COLOR + '[PROXY] %(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# HTTP request handler
class ProxyHandler(SimpleHTTPRequestHandler):
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

    def detect_header_manipulation(self):
        # Define headers that should not be present in legitimate requests
        blacklisted_headers = {
            'X-Forwarded-Host',
            'X-Host',
            'X-Forwarded-For', 
            'X-Real-IP',
            'X-Forwarded-Proto'
        }

        current_headers = set(self.headers.keys())

        # Check if any blacklisted headers are present
        blacklisted_present = blacklisted_headers & current_headers
        if blacklisted_present:
            logger.warning(f"Header manipulation detected: {blacklisted_present}")
            return True
        return False

    def do_GET(self):
        self.log_request_details()

        # Log the Host header value
        host_header = self.headers.get('Host', '')
        logger.info(f"Host header received: {host_header}")

        # Detect if there is any header manipulation
        if self.detect_header_manipulation():
            logger.info("Header manipulation detected. Returning simulated vulnerable response.")
            # Use the Host header value and return simulated vulnerable response
            response_content = get_vulnerable_response(host_header)
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('X-Injected-Header', 'vulnerable')
            self.send_header('X-Host', host_header) 
            self.end_headers()
            self.wfile.write(response_content.encode())
            logger.info("Sent simulated vulnerable response")
        else:
            try:
                # Use Docker service name
                target_url = f"https://https_server:4434{self.path}"
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

# Define server handler
class Handler(Enum):
    PROXY = ProxyHandler

# Run HTTP server
def run_server(address: str, port: int, handler: Handler):
    context = get_ssl_context(f"{os.path.dirname(os.path.realpath(__file__))}/cert.pem", f"{os.path.dirname(os.path.realpath(__file__))}/key.pem")

    httpd = HTTPServer((address, port), handler.value)
    httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
    logger.info(f"Starting proxy server on {address}:{port}")
    httpd.serve_forever()

# Main entry point
if __name__ == "__main__":
    run_server("0.0.0.0", 4433, Handler.PROXY)  # Use 0.0.0.0 to listen on all interfaces within the container
