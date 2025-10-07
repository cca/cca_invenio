# Deployment

We use `helm` for deployment to staging and production instances, see the [cca/invenio-helm](https://github.com/cca/invenio-helm) repo.

```sh
cd path/to/invenio-helm
cd charts
vim set_secrets.sh # add passwords
./deploy.sh
```

The deploy script uninstalls the chart if it exists before reinstalling. The chart uses StatefulSets so data is not lost. If not already done, we should change the `invenio.init` value to be `False` as it will fail when upgrading an existing instance.

## Secrets

Running Invenio in helm requires TLS and image pull secrets. We also need a service account with access to the Google Secret Manager (GSM) to read secret and instance-specific configuration values.

### Image Pull Secret

The helm values.yaml uses `imagePullSecrets` fields to authenticate with our docker registry, these fields are the name of a kubernetes docker-registry secret in the app's namespace. We use a service account with read-only permissions to authenticate with the registry with a JSON key.

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
    --role="roles/artifactregistry.reader" \
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

### TLS Secret

Invenio is designed to run only on HTTPS. The helm chart doesn't work without a TLS secret that configures the load balancer's HTTPS certificate. We use a wildcard certificate for `*.cca.edu` that is managed by SRE. The secret name is set in the helm values file under `ingress.tlsSecretNameOverride`.

`kubectl -ninvenio-dev create secret tls wildcard-cca-edu-tls --cert=/path/to/wildcard.cca.edu.pem --key=/path/to/wildcard.cca.edu.key`

### Google Secret Manager

Create a Service Account with the "Secret Manager Secret Accessor" role, see [configure > secret manager](./configure.md#secret-manager) for details. Save the JSON key to a key.json file, then run `kubectl -ninvenio-dev create secret generic gsm-credentials --from-file=key.json=./key..json`. This is referenced in the Helm chart in the `invenio.extra_env_from_secret` field.

## Links

https://inveniordm.docs.cern.ch/operate/ops/deploy/

https://github.com/inveniosoftware/helm-invenio

https://discord.com/channels/692989811736182844/1034787528735215628
