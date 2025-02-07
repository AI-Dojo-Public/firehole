# SMB proxy

Proxy will intercept any base communication.

## Configuration

* **type**: type of the proxy, only `smb` is an option
* **host**: host to use (e.g. `0.0.0.0`)
* **port**: port to use (e.g. `4455`)
* **origin_host**: host to forward to 127.0.0.1 (e.g. `127.0.0.1`)
* **origin_port**: port to forward to (e.g. `445`)
* **vulnerabilities**: list of vulnerabilities (e.g. `[CVE-2024-99999]`)

**Example:**

```yaml
  - type: smb
    host: 0.0.0.0
    port: 4455
    origin_host: 127.0.0.1
    origin_port: 445
    vulnerabilities:
      - CVE-2024-99999

```

## Test the proxy

Connect to the proxy with an SMB client like you would normally do.
