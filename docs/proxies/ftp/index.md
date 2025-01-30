# FTP proxy

Proxy will intercept any base communication, as well as communication from EPSV mode.

## Configuration

* **type**: type of the proxy, only `ftp` is an option
* **host**: host to use (e.g. `0.0.0.0`)
* **port**: port to use (e.g. `21`)
* **origin_host**: host to forward to 127.0.0.1 (e.g. `127.0.0.1`)
* **origin_port**: port to forward to (e.g. `2121`)
* **vulnerabilities**: list of vulnerabilities (e.g. `[CVE-2011-2523]`)

**Example:**

```yaml
  - type: ftp
    host: 0.0.0.0
    port: 21
    origin_host: 127.0.0.1
    origin_port: 2121
    vulnerabilities:
      - cve-2011-2523

```

## Test the proxy

Connect to the proxy with an FTP client like you would normally do.
