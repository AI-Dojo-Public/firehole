This page contains information about creating and using self-signed certificates. It is all optional.

## Generate private key and self-signed certificate

The following command generates a private key and a self-signed certificate:
```shell
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -noenc
```

In case your application/server has multiple names/addresses, specify the `subjectAltName` parameter.  
Here is an example of an application accessible on `localhost` and `127.0.0.1`:

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
```

### Root CA, intermediate cert, server + client certs

Here are some advanced guides for a reference:

- [Official guide](https://openssl-ca.readthedocs.io/en/latest/introduction.html)
- [Unofficial guide](https://www.golinuxcloud.com/openssl-create-certificate-chain-linux/)
- [Install the certificate system-wide](https://ubuntu.com/server/docs/install-a-root-ca-certificate-in-the-trust-store#install-a-pem-format-certificate)

## Troubleshooting

To use certificate with cURL:
```shell
curl --cacert /path/to/cert.pem
```
