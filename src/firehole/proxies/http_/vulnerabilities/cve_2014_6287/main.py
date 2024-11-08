import subprocess
from requests.structures import CaseInsensitiveDict

from firehole.abstract.vulnerability import VulnerabilityAbstract
from firehole.proxies.http_.proxy import RequestHandler
from urllib.parse import urlparse, parse_qs


class Vulnerability(VulnerabilityAbstract):
    def __init__(self, handler: RequestHandler):
        """
        Vulnerability for CVE-2014-6287.
        :param handler: RequestHandler for the current request
        """
        self._handler = handler
        self._logger = handler.logger.bind(cve="CVE-2014-6287")

    def get_command_from_query(self) -> str | None:
        """
        Get the value (command) from the first parameter from the query.
        :return: Command
        """
        self._logger.debug("Trying to detect a command in the request")
        parsed_url = urlparse(self._handler.path)
        query_parameters = parse_qs(parsed_url.query)
        if query_values := query_parameters.values():
            self._logger.info("Command found in the query")
            return next(iter(query_values))[0]

        return None

    def execute_command(self, command: str) -> bytes:
        """
        Execute the command on the local host.
        :param command: Desired command
        :return: STDOUT and STDERR from the execution
        """
        self._logger.debug("Executing command", command=command)
        try:
            return subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            return e.output

    def check_and_exploit(self) -> bool:
        """
        Check if the request uses the vulnerability and exploit in case it does.
        :return: True in case the vulnerability was used
        """
        if command := self.get_command_from_query():
            output = self.execute_command(command)
            self._handler.send_full_response(200, CaseInsensitiveDict({"Content-Type": "text/plain"}), output)
            return True

        return False
