# FireHole

## Generating certificates
The following command generates a private key and a self-signed certificate for a web application served at localhost. **Make sure to specify a correct `Common Name` and `subjectAltName`**.
```shell
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -noenc -addext "subjectAltName = DNS:localhost, IP:127.0.0.1" <<EOF
CZ
Czechia
Brno
AI DOJO
AI DOJO
localhost
ai@mojo.dojo
EOF
cat cert.pem key.pem > cert-and-key.pem
mv *.pem src/firehole/http_s/
```

### Create Root CA, intermediate cert, server + client certs
Optional for now.

- [Official guide](https://openssl-ca.readthedocs.io/en/latest/introduction.html)
- [Unofficial guide](https://www.golinuxcloud.com/openssl-create-certificate-chain-linux/)

### Install certificates to the system
Optional for now.

To install the certificate system-wide follow [this tutorial](https://ubuntu.com/server/docs/install-a-root-ca-certificate-in-the-trust-store#install-a-pem-format-certificate).

## Installation
Use [Poetry](https://python-poetry.org/) to install the project
```shell
poetry install
```

## Run the application
Copy the generated certificates into the http repository.

Run the main file (test and proxy server)
```shell
poetry run python src/firehole/main.py
```

## Test the proxy
Send a GET request
```shell
curl https://localhost:4433/test --cacert src/firehole/http_s/cert.pem
```
