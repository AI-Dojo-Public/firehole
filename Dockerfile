FROM python:3.12-slim AS base

ENV POETRY_VIRTUALENVS_IN_PROJECT=true

WORKDIR /app

RUN pip install poetry

# Install dependencies
COPY poetry.lock pyproject.toml ./
RUN poetry install --no-root --no-interaction --no-ansi --without dev

# Install app
COPY . .
RUN poetry install --only-root --no-interaction --no-ansi

FROM python:3.12-slim AS production

COPY --from=base /app /app
COPY config.yml /

RUN ln -s /app/.venv/bin/firehole /usr/local/bin/firehole

ENTRYPOINT [ "firehole" ]
CMD [ "/config.yml" ]
