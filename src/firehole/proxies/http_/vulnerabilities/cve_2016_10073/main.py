import os
from requests.structures import CaseInsensitiveDict

from firehole.abstract.vulnerability import VulnerabilityAbstract
from firehole.proxies.http_.proxy import RequestHandler


class Vulnerability(VulnerabilityAbstract):
    # All headers are lowercase since the RequestHandler uses CaseInsensitiveDict
    blacklisted_headers = {"x-forwarded-host", "x-host", "x-forwarded-for", "x-real-ip", "x-forwarded-proto"}

    def __init__(self, handler: RequestHandler):
        """
        Vulnerability for CVE-2016-10073.
        :param handler: RequestHandler for the current request
        """
        self._handler = handler
        self._logger = handler.logger.bind(cve="CVE-2016-10073")

    def create_vulnerable_response(self, host_header: str) -> bytes:
        """
        Create a simulated response.
        :param host_header: Literally the `host` header
        :return: Fabricated response
        """
        self._logger.debug("Creating vulnerable response")
        response_file = os.path.join(os.path.dirname(__file__), "vulnerable_response.html")
        with open(response_file, "r") as file:
            html_content = file.read()

        return html_content.format(host_header=host_header).encode()

    def detect_forbidden_headers(self) -> bool:
        """
        Detect if the request contains forbidden headers.
        :return: True in case it does
        """
        self._logger.debug("Trying to detect forbidden headers in the request")
        if blacklisted_present := self.blacklisted_headers & set(self._handler.headers.keys()):
            self._logger.info("Header manipulation detected", manipulated_headers=blacklisted_present)
            return True

        return False

    def check_and_exploit(self) -> bool:
        """
        Check if the request uses the vulnerability and exploit in case it does.
        :return: True in case the vulnerability was used
        """
        if self.detect_forbidden_headers():
            host_header = self._handler.headers.get("host", "")
            content = self.create_vulnerable_response(host_header)
            headers = CaseInsensitiveDict(
                {"Content-Type": "text/html", "X-Injected-Header": "vulnerable", "X-Host": host_header}
            )
            status_code = 200
            self._handler.send_full_response(status_code, headers, content)
            return True

        return False
