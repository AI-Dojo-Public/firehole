# FireHole

## Docker

**Added SSL Certificate Generation**: Includes steps to generate a self-signed SSL certificate and private key directly within the Dockerfile using OpenSSL. The certificate is configured with subject alternative names for `proxy_server` and `https_server`.

##### Setup and Execution

To build and run the container, including the SSL certificate generation, use the following command:

```
docker-compose up --build
```

This command will build the Docker images, create the necessary SSL certificates, and start the services as defined in the `docker-compose.yml` file.

Both services can be accessed via the following URLs:

- **Proxy Server:** https://localhost:4433/
- **HTTPS Server:**  https://localhost:4434/

For more detailed information on SSL certificate generation, please refer to the documentation [here](https://gitlab.ics.muni.cz/ai-dojo/firehole/-/blob/master_cpy/README.md?ref_type=heads).

## Metasploit Detection

To set up and use the Metasploit module `scanner/http/host_header_injection` for detecting HTTP Host Header Injection vulnerabilities, follow these steps:

### Start Metasploit Framework Console

Open your terminal and start the Metasploit console by typing:

```
msfconsole
```

### Load the Module

Load the `scanner/http/host_header_injection` module:

```
use auxiliary/scanner/http/host_header_injection
```

### Configure the Module

Set the required options for the module:

- **RHOSTS**: The target IP address or range.
- **RPORT**: The port on which the target is running.
- **SSL**: Set to `true` if the target is using HTTPS.

Example configuration:

```
set RHOSTS 127.0.0.1
set RPORT 4433
set SSL true
```

### Run the Module

Execute the scan with:

```
run
```

## Create proxy

Create a new Python package inside the `firehole` package with the name of the proxy (for example an FTP proxy will be called `ftp`). Inside the package directory create a Python file (for example `proxy.py`). This file will contain a class derived from the `firehole.abstract.proxy.ProxyAbstract`.

Additionally create a `vulnerabilities` package inside the proxy package directory (for our example `firehole/ftp/vulnerabilities`), which will contain CVE implementations for the proxy.

Proxy file example:
```python
from firehole.abstract.proxy import ProxyAbstract


class ProxyFTP(ProxyAbstract):
    def __init__(self):
        pass

    def start(self):
        pass

```


Vulnerability file example:
```python
from firehole.abstract.vulnerability import VulnerabilityAbstract


class Vulnerability(VulnerabilityAbstract):
    def __init__(self, request: Request):
        self.request = request

    def is_vulnerable(self):
        return True

    def check(self) -> bool:
        if self.is_vulnerable():
            return True
        return False

```
