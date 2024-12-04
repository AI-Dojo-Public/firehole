# HTTP proxy

Currently, accepts GET requests only.

## Configuration

* **type**: type of the proxy, only `http` is an option
* **host**: host to use (e.g. `0.0.0.0`)
* **port**: port to use (e.g. `80`)
* **origin_host**: host to forward to 127.0.0.1 (e.g. `127.0.0.1`)
* **origin_port**: port to forward to (e.g. `8000`)
* **certificate**: path to the certificate file (e.g. `/path/cert.pem`)
* **private_key**: path to the private key file (e.g. `/path/key.pem`)
* **vulnerabilities**: list of vulnerabilities (e.g. `[CVE-2016-10073]`)

**Example:**

```yaml
applications:
  - type: http
    host: 0.0.0.0
    port: 80
    origin_host: 127.0.0.1
    origin_port: 8000
    vulnerabilities:
      - CVE-2016-10073
      - CVE-2014-6287

```

## Test the proxy

Send a request using cURL or access it using browser ([click here](http://localhost/)).

```shell
curl http://localhost/
```
