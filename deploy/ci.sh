#!/usr/bin/env bash

# Bash strict mode https://olivergondza.github.io/2019/10/01/bash-strict-mode.html
set -euox pipefail
IFS=$'\n\t'

ACTION=${1}

# Functions
delete() {
    if [[ "${ENVIRONMENT}" = "dev" ]]; then
        header "Deleting local kubernetes deployment"
        helm delete --ignore-not-found --namespace "${APP_NAME}-${ENVIRONMENT}" "${APP_NAME}"
        # helm refuses to delete this pvc & `helm install/upgrade` fail if it exists
        kubectl delete --namespace "${APP_NAME}-${ENVIRONMENT}" pvc shared-volume
    else
        echo "Deleting to ${ENVIRONMENT} kubernetes cluster not implemented"
        exit
    fi
}

deploy() {
    if [[ "${ENVIRONMENT}" != "dev" ]]; then
        echo "Deploying to kubernetes not implemented yet"
        exit

        # TODO staging and prod deployments
        # TODO is auth needed with imagePullSecrets?
        gcloud_auth
        gcloud_kubernetes_auth
        # helm chart cannot be installed so we clone it. Repo also has no tags so we checkout a commit
        git clone --shallow-since="2024-02-14" --quiet https://github.com/inveniosoftware/helm-invenio /tmp/helm-invenio
        git -C /tmp/helm-invenio checkout f507397fbb75e3d95d8338959e61542c1c97e633
        INVENIO_HELM_CHART="/tmp/helm-invenio"
    fi

    envsubst < deploy/values.yaml \
        | helm upgrade --install --namespace "${APP_NAME}-${ENVIRONMENT}" --create-namespace --values - "${APP_NAME}" "${INVENIO_HELM_CHART}"
}

docker_build_and_push() {
    header "Building and pushing Docker image"

    # CI push so we have to auth
    if [[ "${ENVIRONMENT}" != "dev" ]]; then
        gcloud_auth
    fi

    # Use Gitlab CI_COMMIT_SHORT_SHA if available, otherwise use current commit
    COMMIT_SHA=${CI_COMMIT_SHORT_SHA:-$(git rev-parse --short=8 HEAD)}
    DOCKER_IMAGE="${GAR_HOSTNAME}/${GCP_PROJECT}/${GAR_REPO}/${APP_NAME}"
    DOCKER_IMAGE_TAG="${DOCKER_IMAGE}:${GAR_IMAGE_TAG}-${COMMIT_SHA}"
    # Pull the latest Docker image
    docker pull --quiet "${DOCKER_IMAGE}:latest" || true
    # Build the Docker image
    # TODO might need --platform linux/arm64 --build-arg BUILDARCH=linux/arm64 to work with minikube
    docker build --build-arg BUILDKIT_INLINE_CACHE=1 --cache-from "${DOCKER_IMAGE}:latest" -t "${DOCKER_IMAGE_TAG}" .
    docker tag  "${DOCKER_IMAGE_TAG}" "${DOCKER_IMAGE}:latest"
    docker push --all-tags ${DOCKER_IMAGE}
}

gcloud_auth() {
    header "Authenticating with GCP"

    # Do not print $GCLOUD_KEY
    set +x

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

# automatically increment staging or release tag then push to git and watch glab ci status -l
release() {
    header "Git tagging for ${ENVIRONMENT} release"

    # get the latest tag
    LATEST_TAG=$(git describe --tags --match "${GIT_TAG_PATTERN}*" --abbrev=0)
    if [[ -z "$LATEST_TAG" ]]; then
        echo "No previous tag found, starting from 0"
        LATEST_TAG_NUMBER="0"
    else
        # get the latest tag number
        LATEST_TAG_NUMBER="${LATEST_TAG//$GIT_TAG_PATTERN-/}"
    fi

    if [[ -z "${LATEST_TAG_NUMBER}" || ! $LATEST_TAG_NUMBER =~ ^[0-9]+$ ]]; then
        echo "Error: cannot parse number from tag ${LATEST_TAG}" >&2
        exit 1
    fi

    # increment the tag number
    NEW_TAG_NUMBER=$((LATEST_TAG_NUMBER + 1))
    NEW_TAG="${GIT_TAG_PATTERN}-${NEW_TAG_NUMBER}"
    echo "Creating new tag: ${NEW_TAG}"
    git tag "${NEW_TAG}"
    git push
    git push origin "${NEW_TAG}"
    sleep 3
    glab ci status --repo california-college-of-the-arts/invenio --live
}

usage() {
    set +x
    echo "Usage: $0 [build|deploy]"
    echo "Requires at least an ENVIRONMENT environment variable to be set to one of [dev, staging, prod]."
}

# Constants
APP_NAME="invenio"
GAR_HOSTNAME="us-west2-docker.pkg.dev"
# TODO pushing dev and staging to the same image might be ruining the cache
GAR_REPO="docker-web"
GCP_ZONE="us-west1-b"

# Environment-dependent variables
case $ENVIRONMENT in
    "dev")
        GCP_PROJECT="cca-web-staging"
        GAR_IMAGE_TAG="dev"
        GIT_TAG_PATTERN="stg-full" # default to staging releases
        ;;
    "staging")
        GCP_PROJECT="cca-web-staging"
        GAR_IMAGE_TAG="staging"
        GIT_TAG_PATTERN="stg-full" # TODO stg-fast
        ;;
    "production")
        GCP_PROJECT="cca-web-0"
        GAR_IMAGE_TAG="prod"
        GIT_TAG_PATTERN="release"
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
    "delete")
        delete
        ;;
    "deploy")
        deploy
        ;;
    "release")
        # automatically increment staging or release tag then push to git and watch glab ci status -l
        release
        ;;
    *)
        echo "Invalid action: ${ACTION}" >&2
        usage
        exit 1
        ;;
esac
