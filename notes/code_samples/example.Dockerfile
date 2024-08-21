# Dockerfile that builds a fully functional image of your app.

FROM alpine:3 AS builder

ARG INVENIO_INSTANCE_PATH=/var/instance
ARG INSTALL_LOCAL_MODULES=0

# set language/locale
ENV LANG=en_US.UTF-8
ENV LANGUAGE=en_US:en
ENV LC_ALL=en_US.UTF-8

# create the instance dir and set it as working directory
RUN mkdir -p "${INVENIO_INSTANCE_PATH}"
WORKDIR ${INVENIO_INSTANCE_PATH}

# install build dependencies
RUN apk update && \
    apk add python3 py3-pip py3-setuptools nodejs npm gcc musl-dev linux-headers python3-dev cairo
RUN pip install --break-system-packages pipenv

# install the python dependencies system-wide
COPY Pipfile Pipfile.lock ./
RUN pipenv install --deploy --system --extra-pip-args="--break-system-packages" && \
    pipenv --clear

# copy the relevant files from the local project directory
COPY ./docker/uwsgi/ ${INVENIO_INSTANCE_PATH}/uwsgi/
COPY ./invenio.cfg ${INVENIO_INSTANCE_PATH}/
COPY ./app_data/ ${INVENIO_INSTANCE_PATH}/app_data/
COPY ./assets/ /tmp/assets/
COPY ./static/ /tmp/static/
COPY ./templates/ /tmp/templates/
COPY ./translations/ /tmp/translations/

# install local modules if specified (for development/testing purposes)
COPY ./local-modules/ ./local-modules/
RUN if [[ -n "${INSTALL_LOCAL_MODULES}" && "${INSTALL_LOCAL_MODULES}" != "0" ]]; then \
        for mod in ./local-modules/*; do \
            if [[ -d "${mod}" ]]; then \
                pip install --break-system-packages "${mod}" || exit 1; \
            fi; \
        done; \
    fi

# collect & build the frontend, and clean up unnecessary source files
# local overrides are copied over before/after the build step so they don't get lost during the build
RUN invenio collect --verbose && \
    mkdir assets templates translations && \
    cp -r /tmp/assets/ ${INVENIO_INSTANCE_PATH}/ && \
    invenio webpack buildall && \
    cp -r /tmp/static/ ${INVENIO_INSTANCE_PATH}/ && \
    cp -r /tmp/templates/ ${INVENIO_INSTANCE_PATH}/ && \
    cp -r /tmp/translations/ ${INVENIO_INSTANCE_PATH}/ && \
    rm -rf ${INVENIO_INSTANCE_PATH}/assets/node_modules && \
    npm cache clean --force


# the actual invenio app image
FROM alpine:3

ARG INVENIO_INSTANCE_PATH=/var/instance
WORKDIR ${INVENIO_INSTANCE_PATH}

# set language/locale
ENV LANG=en_US.UTF-8
ENV LANGUAGE=en_US:en
ENV LC_ALL=en_US.UTF-8
ENV INVENIO_INSTANCE_PATH=/var/instance

# install the runtime dependencies
RUN apk update && \
    apk add python3 py3-setuptools imagemagick font-dejavu cairo

# copy over the built application
COPY --from=builder /usr/bin/invenio /usr/bin
COPY --from=builder /usr/bin/celery /usr/bin
COPY --from=builder /usr/bin/uwsgi /usr/bin
COPY --from=builder "${INVENIO_INSTANCE_PATH}" "${INVENIO_INSTANCE_PATH}"
COPY --from=builder /usr/lib/python3.12/site-packages /usr/lib/python3.12/site-packages

ENTRYPOINT [ "sh", "-c"]