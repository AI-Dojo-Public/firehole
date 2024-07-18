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
```

### Create Root CA, intermediate cert, server + client certs

- [Official guide](https://openssl-ca.readthedocs.io/en/latest/introduction.html)
- [Unofficial guide](https://www.golinuxcloud.com/openssl-create-certificate-chain-linux/)

### Install certificates to the system
To install the certificate system-wide follow [this tutorial](https://ubuntu.com/server/docs/install-a-root-ca-certificate-in-the-trust-store#install-a-pem-format-certificate).
