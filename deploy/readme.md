# Deployment

Set an `ENVIRONMENT` variable to either `staging` or `prod` to deploy to each respective environment. The outline below is aspirational—parts that haven't been implemented yet are noted with `TODO`.

```sh
export ENVIRONMENT=staging
git commit ...
./deploy/ci.sh release # increments tag and pushes, triggering CI/CD pipeline
export ENVIRONMENT=prod
./deploy/ci.sh release # TODO uses prod tag
```

Tags pushed with `release` in them trigger production deployments. Tags pushed with `stg` in them trigger staging deployments.

`./deploy/ci.sh` wraps our docker build and helm deployment commands. You can run particular steps manually.

```sh
export ENVIRONMENT=staging
./deploy/ci.sh build # build and push docker image to staging registry
./deploy/ci.sh deploy # TODO deploy to staging
```

## Links

https://inveniordm.docs.cern.ch/deploy/

https://github.com/inveniosoftware/helm-invenio

https://discord.com/channels/692989811736182844/1034787528735215628
