# Dockerfile that builds a fully functional image of your app.
#
# This image installs all Python dependencies for your application. It's based
# on AlmaLinux with Python 3 (https://github.com/inveniosoftware/docker-invenio)
# and includes Pip, Pipenv, Node.js, NPM and some few standard libraries
# Invenio usually needs.
#
# TODO https://vsupalov.com/buildkit-cache-mount-dockerfile/

FROM registry.cern.ch/inveniosoftware/almalinux:1

COPY Pipfile Pipfile.lock ./
ENV PIPENV_CACHE_DIR /root/.cache/pipenv
RUN mkdir -p ${PIPENV_CACHE_DIR}
RUN --mount=type=cache,target=/root/.cache/pipenv pipenv install --deploy --system

COPY ./docker/uwsgi/ ${INVENIO_INSTANCE_PATH}
COPY ./invenio.cfg ${INVENIO_INSTANCE_PATH}
COPY ./templates/ ${INVENIO_INSTANCE_PATH}/templates/
COPY ./app_data/ ${INVENIO_INSTANCE_PATH}/app_data/
COPY ./ .

RUN cp -r ./static/. ${INVENIO_INSTANCE_PATH}/static/
RUN cp -r ./assets/. ${INVENIO_INSTANCE_PATH}/assets/
RUN invenio collect
RUN invenio webpack create
RUN invenio webpack install --unsafe
RUN invenio webpack build

ENTRYPOINT [ "bash", "-c"]
