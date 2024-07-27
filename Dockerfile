FROM python:3.11.1 as build

RUN pip install --no-cache poetry 

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create true && \
    poetry config virtualenvs.in-project true && \
    poetry install --no-dev

FROM python:3.11.1-slim

COPY --from=build .venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY src src

ENTRYPOINT ["python", "src/main.py", "--config", "aiodocker_config.yaml"]