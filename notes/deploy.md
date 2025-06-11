# Deployment

We use `helm` for deployment to staging and production instances, see the [cca/invenio-helm](https://github.com/cca/invenio-helm) repo.

These notes are partial and we will need to update them once we figure out more.

## Helm

Running Invenio in helm requires TLS and image pull secrets, see below. Outline:

```sh
set NS invenio-dev
kubectl create ns $NS
# create secrets in ns
helm install -f path/to/cca-values.yml invenio path/to/invenio-helm/charts/invenio --version 0.7.0 --namespace $NS
```

The values files may need some `--set` flags for passwords like postgres.

## Creating Helm TLS

App won't run without TLS which is set in `ingress.tlsSecretNameOverride` in values.yml. Get cert files from SRE.

```sh
kubectl -ninvenio-dev create secret tls wildcard-cca-edu-tls --cert=/path/to/wildcard.cca.edu.pem --key=/path/to/wildcard.cca.edu.key
```

## Creating Helm imagePullSecrets

The helm values.yaml uses `imagePullSecrets` fields to authenticate with our docker registry, these fields are the name of a kubernetes docker-registry secret in the app's namespace. We use a service account with read/write permissions to authenticate with the registry with a JSON key.

```fish
set NS invenio-dev
set APP invenio
set PROJECT cca-web-staging
set SA $APP-image-pull
set SA_EMAIL $SA@$PROJECT.iam.gserviceaccount.com
set GAR_LOCATION us-west2
set GAR_REPO docker-web

gcloud iam service-accounts create $SA --project $PROJECT \
    --display-name "Invenio Image Pull"
    --description "AR admin to pull Invenio images"

gcloud artifacts repositories add-iam-policy-binding $GAR_REPO \
    --project=$PROJECT \
    --location=$GAR_LOCATION \
    --role="roles/artifactregistry.writer" \
    --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL"

gcloud iam service-accounts keys create key.json --iam-account=$SA_EMAIL
# (cat key.json) is fish shell subshell not bash
kubectl create secret docker-registry image-pull-secret \
  --docker-server=$GAR_LOCATION-docker.pkg.dev \
  --docker-username=_json_key \
  --docker-password=(cat key.json) \
  --docker-email=$SA_EMAIL \
  --namespace=$NS \
  && rm key.json
```

## Links

https://inveniordm.docs.cern.ch/deploy/

https://github.com/inveniosoftware/helm-invenio

https://discord.com/channels/692989811736182844/1034787528735215628
