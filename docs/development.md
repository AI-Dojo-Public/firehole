## Installing with Poetry

Use [Poetry](https://python-poetry.org/) to install the project:
```shell
poetry install
```

Optionally, enter the Python environment:
```shell
poetry shell
```

## Debugging

To run the application in debug mode, export the `FIREHOLE_DEBUG` variable.

```shell
export FIREHOLE_DEBUG=true
```

## How to create proxy with vulnerability
To make it easier, copy the example **proxy** from the [examples](https://gitlab.ics.muni.cz/ai-dojo/firehole/-/tree/master/examples/) directory to the `src/firehole/proxies/` directory.

### Modifying the proxy
Once you have copied the example, update the following:

* rename the newly copied proxy directory/package to the desired name (e.g. rename the `proxy` to `ftp`)
* rename the class name of the proxy in the `proxy.py` file (e.g. rename the `ProxyNew` to `ProxyFTP`)
* update the `firehole.proxies.__init__.Proxy` enum with a reference to your proxy class

Now you're free to update the proxy as you please.

### Modifying the vulnerability
Once you have copied the example, update the following:

* rename the newly copied vulnerability directory/package to the desired name (e.g. rename the `vulnerability` to `cve_123_456`)
* update the `check_and_exploit` method to do your biding

Make sure to not change the default structure, since the vulnerability import looks like this `vulnerabilities.<vulnerability name>.main.Vulnerability`. Other than that you're free to do as you'd like.

### Testing
Our new proxy and vulnerability can be tested with the following config (in case you've followed the previous steps, otherwise update the config to your needs):
```yaml
applications:
  - type: ftp
    host: 0.0.0.0
    port: 8000
    vulnerabilities:
      - cve_123_456

```

## Best practices

### Logging

When it comes to logging, please take an inspiration from the http proxy:

* assign id for each request the proxy accepts and add it to the log
* once the request enters the vulnerability, add its cve/id to the log

[//]: # (## Testing)
