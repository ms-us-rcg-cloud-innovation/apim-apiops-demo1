# GitHub-side setup

One-time steps you (the user) need to perform after I push the code. Everything Azure-side is already provisioned — only GitHub configuration is left.

---

## 1. Create the private repo and push

I'll do this for you with `gh`:

```bash
cd apim-apiops-demo1
gh repo create ms-us-rcg-cloud-innovation/apim-apiops-demo1 --private --source=. --remote=origin --push
```

(or run it manually if you want to inspect the repo first).

---

## 2. Create the two GitHub teams

Visit https://github.com/orgs/ms-us-rcg-cloud-innovation/teams/new and create:

- `team-catalog` — add the developers who should own the catalog APIs
- `team-orders`  — add the developers who should own the orders API

These names are referenced by `.github/CODEOWNERS`. If you use different names, update CODEOWNERS accordingly.

---

## 3. Set up OIDC federation for Azure (no secrets!)

This lets GitHub Actions log in to Azure without storing a client secret.

### 3a. Create the App Registration / Service Principal

```bash
APP_NAME=apim-apiops-demo1-publisher
SUB=6ec1a899-f785-46d6-b462-21e6659aaccf

# create the app
APP_ID=$(az ad app create --display-name "$APP_NAME" --query appId -o tsv)
SP_OBJECT_ID=$(az ad sp create --id "$APP_ID" --query id -o tsv)
TENANT_ID=$(az account show --query tenantId -o tsv)

# grant Contributor on the APIM RG (publisher needs to update APIM)
az role assignment create --assignee "$APP_ID" \
  --role "Contributor" \
  --scope "/subscriptions/$SUB/resourceGroups/apim-workshops"

echo "AZURE_CLIENT_ID=$APP_ID"
echo "AZURE_TENANT_ID=$TENANT_ID"
echo "AZURE_SUBSCRIPTION_ID=$SUB"
```

### 3b. Create the federated credentials (one per workflow trigger you care about)

```bash
APP_ID=<from above>
REPO=ms-us-rcg-cloud-innovation/apim-apiops-demo1

# main branch (publish workflows)
az ad app federated-credential create --id "$APP_ID" --parameters '{
  "name": "github-main",
  "issuer": "https://token.actions.githubusercontent.com",
  "subject": "repo:'"$REPO"':ref:refs/heads/main",
  "audiences": ["api://AzureADTokenExchange"]
}'

# manual workflow_dispatch on any branch (extractor + manual publish)
az ad app federated-credential create --id "$APP_ID" --parameters '{
  "name": "github-environment-prod",
  "issuer": "https://token.actions.githubusercontent.com",
  "subject": "repo:'"$REPO"':environment:prod",
  "audiences": ["api://AzureADTokenExchange"]
}'

# extractor PR creation
az ad app federated-credential create --id "$APP_ID" --parameters '{
  "name": "github-pull-request",
  "issuer": "https://token.actions.githubusercontent.com",
  "subject": "repo:'"$REPO"':pull_request",
  "audiences": ["api://AzureADTokenExchange"]
}'
```

---

## 4. Create the `prod` GitHub environment

`Settings → Environments → New environment → name: prod`. Optionally add **required reviewers** for production publishes.

---

## 5. Repo secrets (Settings → Secrets and variables → Actions)

| Secret | Value |
| ------ | ----- |
| `AZURE_CLIENT_ID`       | `$APP_ID` from step 3a |
| `AZURE_TENANT_ID`       | `$TENANT_ID` from step 3a |
| `AZURE_SUBSCRIPTION_ID` | `6ec1a899-f785-46d6-b462-21e6659aaccf` |
| `APIM_RG`               | `apim-workshops` |
| `APIM_NAME`             | `apim-networked-a` |

---

## 6. Branch protection on `main`

`Settings → Branches → Add rule` for `main`:
- ✅ Require a pull request before merging
- ✅ Require approvals (1+)
- ✅ **Require review from Code Owners** — this is what gives you per-team gating
- ✅ Require status checks to pass (optional: pick a lint or schema check if you add one)
- ✅ Do not allow bypassing

---

## 7. Register the self-hosted runner on the VM

The publisher must run inside the APIM vnet because APIM is in Internal mode. I already provisioned the VM:

- **VM**: `apimkt-runner-vm`
- **RG**: `apimKT`
- **Public IP**: `64.236.206.204`
- **Private IP** (in vnet `networkhub2/sub1`): `172.30.1.5`
- **SSH key**: `keys/apimkt-runner` (in this directory)
- **OS user**: `azureuser`

### 7a. Get a registration token

GitHub UI: `Settings → Actions → Runners → New self-hosted runner → Linux`. Copy the `--token` value (valid 1 hour).

./config.sh --url https://github.com/ms-us-rcg-cloud-innovation/apim-apiops-demo1 --token AT6JEQ736RY54TO7YJB7SO3J6EUQ2
### 7b. SSH in and install

```bash
ssh -i keys/apimkt-runner azureuser@64.236.206.204
```

On the VM:

```bash
sudo apt-get update && sudo apt-get install -y curl jq

# Install runner
mkdir -p ~/actions-runner && cd ~/actions-runner
RUNNER_VERSION=2.319.1
curl -sSLO https://github.com/actions/runner/releases/download/v${RUNNER_VERSION}/actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz
tar xzf actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz

./config.sh \
  --url https://github.com/ms-us-rcg-cloud-innovation/apim-apiops-demo1 \
  --token AT6JEQ736RY54TO7YJB7SO3J6EUQ2 \
  --name apimkt-runner-vm \
  --labels self-hosted,apim-vnet \
  --unattended

sudo ./svc.sh install
sudo ./svc.sh start
sudo ./svc.sh status
```

The label `apim-vnet` is what the workflows target via `runs-on: [self-hosted, apim-vnet]`.

### 7c. Install Azure CLI on the runner (publisher uses `az login` via OIDC)

```bash
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
az --version
```

That's it — workflows on the runner can now `azure/login@v2` with the federated credentials and reach APIM via its private endpoint.

---

## 8. First run

1. Go to **Actions → Run APIOps Extractor → Run workflow**.
2. It SSHes into APIM via the runner, dumps the current state into `apimartifacts/`, opens a PR.
3. Review and merge the PR. CODEOWNERS will route reviews to the right team(s).
4. From now on, edits in `apimartifacts/apis/catalog-*` will trigger only `publish-team-catalog`, and edits in `apimartifacts/apis/orders-real-api/` will trigger only `publish-team-orders`.

---

## 9. Day-2 ops

- **Adding a new API to a team**: edit `configurations/configuration.<team>.yaml` and add the API name. Add CODEOWNERS lines for the new path. Re-run extractor or push the new artifact.
- **Rotating a function key**: regenerate via Azure portal/CLI, update the named value via the portal/CLI, then run extractor to bring `apimartifacts/named values/<name>` back in sync (the publisher won't overwrite the secret value during a routine push, but it tracks all other metadata).
- **Promoting to a second APIM**: copy `apimartifacts/` and add a `configuration.prod.yaml`, point the publisher at a different APIM service via secrets in a `prod-east` environment.
