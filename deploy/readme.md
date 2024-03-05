# Deployment

Copy example.env to .env and fill in values. An `ENVIRONMENT` variable should be set to one of `dev` (local minikube), `staging`, or `prod`. If you `pipenv shell` then pipenv automatically loads values in .env files. The outline below is aspirational—parts that haven't been implemented yet are noted with `TODO`.

```sh
pipenv shell # loads .env with ENVIRONMENT=dev
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

## Links

https://inveniordm.docs.cern.ch/deploy/

https://github.com/inveniosoftware/helm-invenio

https://discord.com/channels/692989811736182844/1034787528735215628
