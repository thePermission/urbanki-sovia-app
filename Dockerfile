## ------------------------------- Builder Stage ------------------------------ ##
FROM python:3.13.3-alpine3.21 AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PROJECT_ENVIRONMENT=/app

RUN --mount=type=cache,target=/root/.cache \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync \
        --locked \
        --no-dev \
        --no-install-project

COPY . /src
WORKDIR /src
RUN --mount=type=cache,target=/root/.cache \
    uv sync \
        --locked \
        --no-dev \
        --no-editable

# build real image
FROM python:3.13.3-alpine3.21 AS image

COPY --from=builder --chown=app:app /app /app

ENV PATH=/app/bin:$PATH

STOPSIGNAL SIGINT

COPY docker-entrypoint.sh /
COPY .streamlit /
RUN chmod +x /docker-entrypoint.sh
WORKDIR /app

ENTRYPOINT ["/docker-entrypoint.sh"]