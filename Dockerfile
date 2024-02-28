# Dockerfile that builds a fully functional image of your app.
#
# This image installs all Python dependencies for your application. It's based
# on Almalinux (https://github.com/inveniosoftware/docker-invenio)
# and includes Pip, Pipenv, Node.js, NPM and some few standard libraries
# Invenio usually needs.
#
# Note: It is important to keep the commands in this file in sync with your
# bootstrap script located in ./scripts/bootstrap.

# https://github.com/inveniosoftware/docker-invenio
# https://registry.cern.ch/harbor/projects/1825/repositories/almalinux/artifacts-tab?publicAndNotLogged=yes
FROM registry.cern.ch/inveniosoftware/almalinux:latest

COPY site ./site
COPY Pipfile Pipfile.lock ./
ENV PIPENV_CACHE_DIR /root/.cache/pipenv
RUN mkdir -p ${PIPENV_CACHE_DIR}
RUN --mount=type=cache,target=/root/.cache/pipenv pipenv install --deploy --system

COPY ./docker/uwsgi/ ${INVENIO_INSTANCE_PATH}
COPY ./invenio.cfg ${INVENIO_INSTANCE_PATH}
COPY ./templates/ ${INVENIO_INSTANCE_PATH}/templates/
COPY ./app_data/ ${INVENIO_INSTANCE_PATH}/app_data/
COPY ./translations/ ${INVENIO_INSTANCE_PATH}/translations/
COPY ./ .

RUN cp -r ./static/. ${INVENIO_INSTANCE_PATH}/static/ && \
    cp -r ./assets/. ${INVENIO_INSTANCE_PATH}/assets/ && \
    invenio collect --verbose  && \
    invenio webpack buildall

ENTRYPOINT [ "bash", "-c"]
