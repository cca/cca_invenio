# Deployment

NOTE: this information is out of date. We need to connect the cca_invenio with our repo for the helm chart.

Copy example.env to .env and fill in values. An `ENVIRONMENT` variable should be set to one of `dev` (local minikube), `staging`, or `prod`. The outline below is aspirational—parts that haven't been implemented yet are noted with `TODO`.

```sh
# TODO load env vars in .env
source .venv/bin/activate.fish
git commit ... && git push # commit changes to code
./deploy/ci.sh deploy # test local deployment
export ENVIRONMENT=staging
./deploy/ci.sh release # increments tag and pushes, triggering CI/CD pipeline
export ENVIRONMENT=prod
./deploy/ci.sh release # TODO uses prod tag
```

Tags pushed with `release` in them trigger production deployments. Tags pushed with `stg` in them trigger staging deployments. `./deploy/ci.sh` wraps our docker build and helm deployment commands. You can run particular steps manually.

```sh
export ENVIRONMENT=staging
./deploy/ci.sh build # build and push docker image to staging registry
./deploy/ci.sh deploy # TODO deploy to staging
```

## Creating Helm imagePullSecrets

The helm values.yaml uses `imagePullSecrets` fields to authenticate with our docker registry, these fields are the name of a kubernetes docker-registry secret in the app's namespace. We use a service account to authenticate with the registry with a JSON key. The easiest way to create the secret is to derive it from docker's config.json file but be careful that the config.json _only has the service account's credentials_ and not your personal ones. This is a general outline:

- Create service account with ability to read/write images in Artifact Registry
- Create a JSON key for the service account, save it to a key.json file
- Run a local container `docker run --rm -it docker:dind sh` or `minikube start && minikube ssh` to get a shell not authenticated with docker
- Login in like `docker login -u _json_key -p "$(cat key.json)" $GAR_HOSTNAME`
- Copy the `~/.docker/config.json` file to the host e.g. `minikube cp minikube:/home/docker/.docker/config.json config.json`
- Create the secret with `kubectl create secret docker-registry regsecret --from-file=.dockerconfigjson=config.json --namespace=$NS`

The other approach would be to create a secret like `kubectl create secret docker-registry regsecret --docker-server=$GAR_HOSTNAME --docker-username=_json_key --docker-password="$(cat key.json)"` but managing newlines in the JSON files might be tricky.

If you are going to transport the secret elsewhere, remember to delete irrelevant or inaccurate properties like `namespace`, `resourceVersion`, `uid`, `creationTimestamp`, and any last-applied-configuration from the kubernetes yaml or json.

## Links

https://inveniordm.docs.cern.ch/deploy/

https://github.com/inveniosoftware/helm-invenio

https://discord.com/channels/692989811736182844/1034787528735215628
