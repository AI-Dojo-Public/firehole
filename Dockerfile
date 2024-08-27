FROM python:3.11-slim

WORKDIR /usr/src/app

# Install Poetry
COPY pyproject.toml poetry.lock ./
RUN pip install poetry
RUN poetry install --no-root

# Copy application code
COPY . .

# Generate SSL certificates
RUN openssl req -x509 -newkey rsa:4096 -keyout src/firehole/http_s/key.pem -out src/firehole/http_s/cert.pem -days 365 -noenc -addext "subjectAltName = DNS:proxy_server, DNS:https_server, IP:127.0.0.1" \
    -subj "/C=CZ/ST=Czechia/L=Brno/O=AI DOJO/OU=AI DOJO/CN=localhost/emailAddress=ai@mojo.dojo"

RUN cat src/firehole/http_s/cert.pem src/firehole/http_s/key.pem > src/firehole/http_s/cert-and-key.pem

EXPOSE 4433 4434

CMD ["poetry", "run", "python", "src/firehole/main.py"]
