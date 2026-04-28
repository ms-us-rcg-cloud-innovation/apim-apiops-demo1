# apim-apiops-demo1

End-to-end demo of [Azure APIOps](https://azure.github.io/apiops/) managing one APIM instance shared by **two development teams**:

| Team           | APIs they own                                |
| -------------- | -------------------------------------------- |
| `team-catalog` | `catalog-products-api`, `catalog-weather-api` |
| `team-orders`  | `orders-real-api`                            |

Each team has its own `configuration.<team>.yaml` and its own publish workflow. CODEOWNERS gates PR approvals so each team can only land changes to its own APIs.

## Repo layout

```
.
├── .github/
│   ├── CODEOWNERS                         # per-team review gates
│   └── workflows/
│       ├── run-extractor.yaml             # manual: pull APIM state -> PR
│       ├── publish-team-catalog.yaml      # auto on push to team-catalog paths
│       └── publish-team-orders.yaml       # auto on push to team-orders paths
├── apimartifacts/                         # populated by extractor (the source of truth)
├── configurations/
│   ├── configuration.team-catalog.yaml    # filters publisher to team-catalog scope
│   └── configuration.team-orders.yaml     # filters publisher to team-orders scope
├── functions/                             # backing Azure Functions source code
│   ├── catalog-products/   (Python v2)
│   ├── catalog-weather/    (Python v2)
│   └── orders/             (Python v2)
└── specs/                                 # OpenAPI 3 specs per API
```

## Backing Azure Functions

Resource group **`apimKT`** (North Central US), Linux App Service Plan `apimkt-plan` (B1):

| Function App                       | Routes                                |
| ---------------------------------- | ------------------------------------- |
| `func-catalog-products-9249`       | `GET /api/products`, `GET /api/products/{id}` |
| `func-catalog-weather-9249`        | `GET /api/weather/{city}`             |
| `func-orders-9249`                 | `GET /api/orders`, `POST /api/orders` |

All require a **function key** (function-level auth). APIM passes it via the `x-functions-key` header from a secret named value.

## How publishing works

1. A team edits artifacts under their own folder (their CODEOWNERS scope) and opens a PR.
2. CODEOWNERS forces review by that team only.
3. On merge to `main`, **only that team's publisher workflow** runs (path filters).
4. The publisher reads `configuration.<team>.yaml` and reconciles **only** the listed APIs/products/named-values/backends — the other team's resources are untouched.

## Self-hosted runner

APIM is in **Internal vnet mode**, so its management plane is only reachable from inside vnet `networkhub2`. The publisher therefore runs on a **self-hosted GitHub Actions runner** on a VM (`apimkt-runner-vm`, private IP `172.30.1.5`) that is in that vnet. Both publish workflows target `runs-on: [self-hosted, apim-vnet]`.

See [`docs/github-setup.md`](docs/github-setup.md) for one-time configuration: creating the GitHub repo, registering the runner, OIDC federation, secrets, branch protection, and CODEOWNERS teams.
