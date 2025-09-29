# Based on invenio-rdm-starter Dockerfile
# https://github.com/front-matter/invenio-rdm-starter/blob/ba0269ff0eec036d5d38408d5fa7184f284036b3/Dockerfile
FROM python:3.13-bookworm AS builder

ENV ENVIRONMENT=dockerbuild \
    LANG=en_US.UTF-8 \
    LANGUAGE=en_US:en

# Install OS package dependencies
RUN --mount=type=cache,sharing=locked,target=/var/cache/apt \
    apt-get update --fix-missing && \
    apt-get install -y --no-install-recommends \
        build-essential \
        cargo \
        curl \
        libffi-dev \
        libssl-dev \
        libxml2-dev \
        libxmlsec1-dev \
        pkg-config \
        python3-dev

# Install Node.js 22.x
RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - && \
    apt-get install -y nodejs --no-install-recommends && apt-get clean

# Install uv and activate virtualenv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
RUN uv venv /opt/invenio/.venv

# Use the virtual environment automatically
# uwsgi must be built without XML or it breaks lxml/xmlsec compatibility
# https://github.com/cca/cca_invenio/issues/39
ENV INVENIO_INSTANCE_PATH=/opt/invenio/var/instance \
    PATH="/opt/invenio/.venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/opt/invenio/.venv \
    UV_PYTHON_DOWNLOADS=0 \
    UWSGI_PROFILE_OVERRIDE="xml=no" \
    VIRTUAL_ENV=/opt/invenio/.venv \
    WORKING_DIR=/opt/invenio

WORKDIR ${INVENIO_INSTANCE_PATH}

COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev --group uwsgi
COPY . .

COPY site ${INVENIO_INSTANCE_PATH}/site
COPY static ${INVENIO_INSTANCE_PATH}/static
COPY assets ${INVENIO_INSTANCE_PATH}/assets
COPY templates ${INVENIO_INSTANCE_PATH}/templates
COPY app_data ${INVENIO_INSTANCE_PATH}/app_data
COPY translations ${INVENIO_INSTANCE_PATH}/translations
COPY ./invenio.cfg ${INVENIO_INSTANCE_PATH}

# Install Python dependencies including local "site" module
RUN --mount=type=cache,target=/root/.cache/uv uv sync --frozen --no-dev --group uwsgi

# Build Javascript assets — `invenio` cmd means we need functional invenio.cfg during build
RUN --mount=type=cache,target=/var/cache/assets invenio collect --verbose && invenio webpack buildall

FROM python:3.13-slim-bookworm AS runtime

ENV LANG=en_US.UTF-8 \
    LANGUAGE=en_US:en

# Install OS package dependencies
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
RUN --mount=type=cache,sharing=locked,target=/var/cache/apt apt-get update -y --fix-missing && \
    apt-get install -y --no-install-recommends \
        apt-transport-https \
        apt-utils \
        curl \
        debian-archive-keyring \
        debian-keyring \
        gpg \
        libcairo2 \
        libxml2 \
        libxmlsec1 \
    && apt-get clean

ENV INVENIO_INSTANCE_PATH=/opt/invenio/var/instance \
    PATH="/opt/invenio/.venv/bin:$PATH" \
    VIRTUAL_ENV=/opt/invenio/.venv \
    WORKING_DIR=/opt/invenio

# Create invenio user and set appropriate permissions
ENV INVENIO_USER_ID=1000
RUN adduser invenio --uid ${INVENIO_USER_ID} --gid 0 --no-create-home --disabled-password

COPY --from=builder --chown=invenio:root ${VIRTUAL_ENV} ${VIRTUAL_ENV}
COPY --from=builder --chown=invenio:root ${INVENIO_INSTANCE_PATH}/site ${INVENIO_INSTANCE_PATH}/site
COPY --from=builder --chown=invenio:root ${INVENIO_INSTANCE_PATH}/static ${INVENIO_INSTANCE_PATH}/static
COPY --from=builder --chown=invenio:root ${INVENIO_INSTANCE_PATH}/assets ${INVENIO_INSTANCE_PATH}/assets
COPY --from=builder --chown=invenio:root ${INVENIO_INSTANCE_PATH}/templates ${INVENIO_INSTANCE_PATH}/templates
COPY --from=builder --chown=invenio:root ${INVENIO_INSTANCE_PATH}/app_data ${INVENIO_INSTANCE_PATH}/app_data
COPY --from=builder --chown=invenio:root ${INVENIO_INSTANCE_PATH}/translations ${INVENIO_INSTANCE_PATH}/translations
COPY --from=builder --chown=invenio:root ${INVENIO_INSTANCE_PATH}/invenio.cfg ${INVENIO_INSTANCE_PATH}/invenio.cfg
# we don't have a setup file
# https://github.com/front-matter/invenio-rdm-starter/blob/main/setup.sh
# COPY ./setup.sh /opt/invenio/.venv/bin/setup.sh

WORKDIR ${WORKING_DIR}/src

USER invenio

EXPOSE 5000
COPY --chown=invenio:root docker/uwsgi/uwsgi_ui.ini uwsgi.ini
CMD ["uwsgi", "--ini", "uwsgi.ini"]
