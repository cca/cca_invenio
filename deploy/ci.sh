#!/usr/bin/env bash

# Bash strict mode https://olivergondza.github.io/2019/10/01/bash-strict-mode.html
set -euox pipefail
IFS=$'\n\t'

ACTION=${1}

if [[ -z "${ENVIRONMENT}" ]]; then
    (>&2 echo "You must set the ENVIRONMENT env var")
    exit 1
fi

# Functions
docker_build_and_push() {
    header "Building and pushing Docker image"
    # Use Gitlab CI_COMMIT_SHORT_SHA if available, otherwise use current commit
    COMMIT_SHA=${CI_COMMIT_SHORT_SHA:-$(git rev-parse --short=8 HEAD)}
    DOCKER_IMAGE="${GAR_HOSTNAME}/${GCP_PROJECT}/${GAR_REPO}/${APP_NAME}"
    DOCKER_IMAGE_TAG="${DOCKER_IMAGE}:${GAR_IMAGE_TAG}-${COMMIT_SHA}"
    # Pull the latest Docker image
    docker pull --quiet "${DOCKER_IMAGE}:latest" || true
    # Build the Docker image
    docker build --build-arg BUILDKIT_INLINE_CACHE=1 --cache-from "${DOCKER_IMAGE}:latest" -t "${DOCKER_IMAGE_TAG}" .
    docker tag  "${DOCKER_IMAGE_TAG}" "${DOCKER_IMAGE}:latest"
    docker push --all-tags ${DOCKER_IMAGE}
}

gcloud_auth() {
    header "Authenticating with GCP"

    # Do not print $GCLOUD_KEY
    set +x

    if [[ -z "${GCLOUD_KEY}" ]]; then
        echo "You must set the GCLOUD_KEY env var"
        exit 1
    fi

    # Install our service account credentials.
    echo "$GCLOUD_KEY" > /tmp/gcloud.json
    gcloud auth activate-service-account --key-file /tmp/gcloud.json

    # Authenticate the Docker daemon
    gcloud --quiet auth configure-docker $GAR_HOSTNAME
}

gcloud_kubernetes_auth() {
    gcloud --project=$GCP_PROJECT container clusters get-credentials -z $GCP_ZONE "$GCP_GKE_CLUSTER_NAME"
}

header() {
    set +x
    echo "========================================================================"
    echo " $1"
    echo "========================================================================"
}

usage() {
    set +x
    echo "Usage: $0 [build|deploy]"
    echo "Requires at least an ENVIRONMENT environment variable to be set to one of [dev/local, staging, prod]."
}

# Constants
APP_NAME="invenio"
GAR_HOSTNAME="us-west2-docker.pkg.dev"
GAR_REPO="docker-web"
GCP_ZONE="us-west1-b"

# Environment-dependent variables
case $ENVIRONMENT in
    "dev" | "local")
        GCP_PROJECT="cca-web-staging"
        GAR_IMAGE_TAG="dev"
        # No need to authenticate with GCP
        ;;
    "staging")
        GCP_PROJECT="cca-web-staging"
        GAR_IMAGE_TAG="staging"
        gcloud_auth
        ;;
    "prod")
        GCP_PROJECT="cca-web-0"
        GAR_IMAGE_TAG="prod"
        gcloud_auth
        ;;
    *)
        (>&2 echo "Invalid environment: ${ENVIRONMENT}")
        exit 1
        ;;
esac

# Main
case $ACTION in
    "help" | "--help" | "-h" | "")
        usage
        ;;
    "build")
        docker_build_and_push
        ;;
    "deploy")
        # helm nonsense
        # cat deploy/values.yaml | envsubst | helm upgrade --install --namespace ${APP_NAME}-${ENVIRONMENT} --create-namespace --values -
        echo "Deploying to kubernetes not implemented yet"
        ;;
    *)
        echo "Invalid action: ${ACTION}" >&2
        usage
        exit 1
        ;;
esac
