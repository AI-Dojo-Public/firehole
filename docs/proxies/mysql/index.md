# MySQL proxy

Proxy will intercept any communication.

## Configuration

* **type**: type of the proxy, only `mysql` is an option
* **host**: host to use (e.g. `0.0.0.0`)
* **port**: port to use (e.g. `3307`)
* **origin_host**: host to forward to 127.0.0.1 (e.g. `127.0.0.1`)
* **origin_port**: port to forward to (e.g. `3306`)
* **vulnerabilities**: list of vulnerabilities (e.g. `[CVE-2012-2122]`)

**Example:**

```yaml
  - type: mysql
    host: 0.0.0.0
    port: 3307
    origin_host: 127.0.0.1
    origin_port: 3306
    vulnerabilities:
      - CVE-2012-2122

```

## Test the proxy

Connect to the proxy with a MySQL client like you would normally do.
