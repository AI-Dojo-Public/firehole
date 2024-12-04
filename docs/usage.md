Before we start Firehole, we need to create a config.  
For this example, we will start with one HTTP proxy with a single vulnerability.

The proxy will run at `http://0.0.0.0:8000` and will forward (almost) all traffic to `http://127.0.0.1:20000`.  
It will also contain an RCE vulnerability (more specifically *CVE-2014-6287*).

```yaml
applications:
  - type: http
    host: 0.0.0.0
    port: 8000
    origin_host: 127.0.0.1
    origin_port: 20000
    vulnerabilities:
      - CVE-2014-6287

```

Once you've saved the configuration to a file (for example `config.yml`), you can start the application:

```shell
firehole /path/to/config.yml
```

## Testing the proxy

To check if the proxy is working, we can either use cURL in terminal or access the page with browser ([click here](http://127.0.0.1:8000/)).

```shell
curl http://127.0.0.1:8000/
```

In case you've specified correct origin host and port, you will see you original page.

Now to test the vulnerability. Specify any query parameter and assign a command as its value.  
Notice: **This will execute a shell command on your machine!**

Once again, we can use either cURL or a browser ([click here](http://127.0.0.1:8000/?param=whoami))

```shell
curl http://127.0.0.1:8000/?param=whoami
```
