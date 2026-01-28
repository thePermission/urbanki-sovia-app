## ------------------------------- Builder Stage ------------------------------ ##
FROM python:3.12.12 as builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Definiere Argumente für den Build-Prozess
ARG HTTP_PROXY
ARG HTTPS_PROXY
ARG NO_PROXY

# Setze Umgebungsvariablen für uv (und andere Tools)
ENV http_proxy=$HTTP_PROXY
ENV https_proxy=$HTTPS_PROXY
ENV no_proxy=$NO_PROXY

RUN mkdir /data
COPY data/model.pth /data/
COPY src /src
COPY README.md /
COPY .streamlit /.streamlit
COPY pyproject.toml /
COPY .python-version /
COPY uv.lock /
RUN uv sync
RUN uv run python -c "import duckdb; \
    import os; \
    proxy = os.getenv('http_proxy'); \
    conn = duckdb.connect(); \
    conn.execute(f\"SET http_proxy='{proxy}'\"); \
    conn.execute(\"INSTALL spatial\");"
COPY docker-entrypoint.sh /
RUN chmod +x /docker-entrypoint.sh
ENTRYPOINT ["/docker-entrypoint.sh"]