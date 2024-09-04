import os


from firehole.utility.logger import logger
from firehole.http_s.vulnerabilities.abstract import VulnerabilityAbstract
from firehole.http_s.proxy import ProxyHandler


class Vulnerability(VulnerabilityAbstract):
    def __init__(self, handler: ProxyHandler):
        self.handler = handler

    def get_vulnerable_response(self, host_header):
        logger.info("Returning simulated vulnerable response content from file.")

        base_dir = os.path.dirname(__file__)
        file_path = os.path.join(base_dir, 'vulnerable_response.html')

        with open(file_path, 'r') as file:
            html_content = file.read()

        response_content = html_content.format(host_header=host_header)

        return response_content

    def detect_header_manipulation(self):
        # Define headers that should not be present in legitimate requests
        blacklisted_headers = {
            'X-Forwarded-Host',
            'X-Host',
            'X-Forwarded-For',
            'X-Real-IP',
            'X-Forwarded-Proto'
        }

        current_headers = set(self.handler.headers.keys())

        # Check if any blacklisted headers are present
        blacklisted_present = blacklisted_headers & current_headers
        if blacklisted_present:
            logger.warning(f"Header manipulation detected: {blacklisted_present}")
            return True
        return False

    def check(self) -> bool:
        if self.detect_header_manipulation():
            logger.info("Header manipulation detected. Returning simulated vulnerable response.")
            host_header = self.handler.headers.get('Host', '')
            content = self.get_vulnerable_response(host_header).encode()
            headers = [('Content-Type', 'text/html'), ('X-Injected-Header', 'vulnerable'), ('X-Host', host_header)]
            code = 200

            self.handler.send_response(code)
            for header in headers:
                self.handler.send_header(*header)
            self.handler.end_headers()
            self.handler.wfile.write(content)

            return True

        return False
