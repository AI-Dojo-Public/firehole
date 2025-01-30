import hashlib
import structlog

from firehole.proxies.mysql.vulnerabilities.vulnerability import MySQLVulnerabilityAbstract


class Vulnerability(MySQLVulnerabilityAbstract):
    def __init__(self, logger: structlog.stdlib.BoundLogger):
        """
        Vulnerability for CVE-2012-2122
        """
        self._logger = logger.bind(cve="CVE-2012-2122")
        self.password = b"wordpress"
        self._greeting_packet: tuple[bytes] | None = None
        self._data: bytes | None = None

    @property
    def data(self) -> bytes | None:
        if self._data:
            return self._data
        return None

    def check_and_exploit(self, data: bytes) -> bool:
        if self._greeting_packet and self._data:
            return False

        if not self._greeting_packet:
            try:
                self._greeting_packet = self.parse_greeting_packet(data)
                self._logger.info("Parsed greeting packet", packet=self._greeting_packet)
            except Exception as ex:
                self._logger.debug("Unable to parse the packet", error=ex)
        else:
            try:
                login_packet = self.parse_login_request_packet(data)
                new_password = self.scramble_caching_sha2(login_packet[8], self._greeting_packet[13])
                self._data = data.replace(login_packet[8], new_password)
                self._logger.info("Login bypass successful")
                return True
            except Exception as ex:
                self._logger.debug("Unable to parse the packet", error=ex)

        return False

    @staticmethod
    def scramble_caching_sha2(password: bytes, nonce: bytes) -> bytes:
        """
        Scramble algorithm used in cached_sha2_password fast path.
        XOR(SHA256(password), SHA256(SHA256(SHA256(password)), nonce))
        """
        p1 = hashlib.sha256(password).digest()
        p2 = hashlib.sha256(p1).digest()
        p3 = hashlib.sha256(p2 + nonce).digest()

        res = bytearray(p1)
        for i in range(len(p3)):
            res[i] ^= p3[i]

        return bytes(res)

    @staticmethod
    def parse_greeting_packet(
        packet: bytes,
    ) -> tuple[bytes, bytes, bytes, bytes, bytes, bytes, bytes, bytes, bytes, bytes, bytes, bytes, bytes, bytes]:
        prefix, rest = packet.split(b"\n", 1)
        version, rest = rest.split(b"\x00", 1)
        tid, rest = rest[0:4], rest[4:]
        salt1, rest = rest.split(b"\x00", 1)
        server_capabilities, rest = rest[0:2], rest[2:]
        language, rest = rest[0:1], rest[1:]
        status, rest = rest[0:2], rest[2:]
        extended_capabilities, rest = rest[0:2], rest[2:]
        auth_plugin_length, rest = rest[0:1], rest[1:]
        unused, rest = rest[0:10], rest[10:]
        salt2, rest = rest.split(b"\x00", 1)
        auth_plugin_string, rest = rest.split(b"\x00", 1)
        whole_salt = salt1 + salt2

        return (
            prefix,
            version,
            tid,
            salt1,
            server_capabilities,
            language,
            status,
            extended_capabilities,
            auth_plugin_length,
            unused,
            salt2,
            auth_plugin_string,
            rest,
            whole_salt,
        )

    @staticmethod
    def parse_login_request_packet(
        packet: bytes,
    ) -> tuple[bytes, bytes, bytes, bytes, bytes, bytes, bytes, bytes, bytes, bytes, bytes]:
        length, rest = packet[0:3], packet[3:]
        packet_number, rest = rest[0:1], rest[1:]
        client_capabilities, rest = rest[0:2], rest[2:]
        extended_client_capabilities, rest = rest[0:2], rest[2:]
        max_packet, rest = rest[0:4], rest[4:]
        charset, rest = rest[0:1], rest[1:]
        unused, rest = rest[0:23], rest[23:]
        username, rest = rest.split(b"\x00", 1)
        pass_len, rest = int.from_bytes(bytes(rest[0:1])), rest[1:]  # works only up to 65535
        password, rest = rest[0:pass_len], rest[pass_len:]
        schema, rest = rest.split(b"\x00", 1)
        auth_plugin, rest = rest.split(b"\x00", 1)

        return (
            length,
            packet_number,
            client_capabilities,
            extended_client_capabilities,
            max_packet,
            charset,
            unused,
            username,
            password,
            schema,
            auth_plugin,
        )
