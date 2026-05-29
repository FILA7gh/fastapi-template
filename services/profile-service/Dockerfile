FROM ghcr.io/astral-sh/uv:python3.12-alpine

RUN apk add --no-cache gettext bash gcc musl-dev python3-dev postgresql-client
RUN mkdir -p /opt/services/profile-service
WORKDIR /opt/services/profile-service


COPY pyproject.toml .

ENV UV_PROJECT_ENVIRONMENT="/usr/local/"

RUN uv sync

COPY . .


RUN chmod +x /opt/services/profile-service/entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["sh", "/opt/services/profile-service/entrypoint.sh"]
