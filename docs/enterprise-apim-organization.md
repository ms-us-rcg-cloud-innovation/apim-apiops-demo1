# How enterprise customers organize APIs and products in Azure API Management

Enterprise customers usually organize **APIs by business or domain ownership** and **products by consumer access model**.

The clean mental model is:

| APIM concept | Enterprise use |
| --- | --- |
| **API** | A technical contract for a backend or domain capability, usually owned by a product team |
| **Product** | A consumable bundle offered to developers or applications, often with subscriptions, quotas, approval, and terms |
| **Subscription** | Access credential for a consumer, application, or team to call one product, one API, or all APIs |
| **Group** | Controls product visibility in the developer portal |
| **Policy** | Enforcement layer for authentication, throttling, transformation, routing, logging, and governance |
| **Workspace** | Optional Premium or Premium v2 federation boundary for teams to manage their own APIs, products, subscriptions, and related resources |

## Common enterprise pattern

| Area | Example |
| --- | --- |
| **APIs by domain/team** | `orders-api`, `catalog-products-api`, `customer-profile-api`, `payments-api` |
| **Products by audience/tier** | `internal-developers`, `partner-basic`, `partner-premium`, `mobile-apps`, `enterprise-integrations` |
| **Subscriptions by app/consumer** | `contoso-mobile-prod`, `sap-order-sync`, `partner-a-sandbox`, `crm-integration-prod` |
| **Groups by audience** | `Internal Developers`, `Partner A`, `Partner B`, `Premium Partners` |
| **Policies by scope** | Global security headers, product-level throttling, API-level auth, operation-level validation |

The key point is that **products are not always the same as APIs**. A product is usually a **business or access package**.

## Example product model

| Product | APIs included | Why |
| --- | --- | --- |
| `Internal Platform APIs` | Orders, Catalog, Customer, Inventory | Internal teams get broad access |
| `Partner Ordering Basic` | Orders read-only, Catalog read-only | External partners can browse and submit limited orders |
| `Partner Ordering Premium` | Orders read/write, Catalog, Inventory availability | Higher quota and more capabilities |
| `Mobile App Backend` | Catalog, Orders, Customer profile | APIs needed by the mobile app |
| `Analytics Consumers` | Reporting APIs only | Separate read-heavy consumers |

## Policy placement by scope

| Policy scope | Enterprise use |
| --- | --- |
| **Global / all APIs** | Correlation IDs, security headers, common logging, baseline CORS, deny unsafe traffic |
| **Workspace / team** | Team-specific governance if using APIM workspaces |
| **Product** | Subscription throttling, quota, approval behavior, terms, partner-specific limits |
| **API** | Backend auth, JWT validation, URL rewrite, named values for backend host or keys |
| **Operation** | Request validation, mock response, transformation, special rate limit on expensive operations |

## Demo explanation

For this APIOps demo, explain the model like this:

> The API represents who owns the backend capability. The product represents how consumers subscribe to or get access to that capability.

Current demo mapping:

| Demo item | Enterprise interpretation |
| --- | --- |
| `catalog-products-api` | Catalog team-owned API |
| `catalog-weather-api` | Catalog team-owned API |
| `orders-real-api` | Orders team-owned API |
| `team-catalog` product | Internal/team product for catalog APIs |
| `team-orders` product | Internal/team product for orders API |
| `team-orders-demo` subscription | A consumer/application subscription key for the orders product |
| CODEOWNERS | GitHub-side ownership control before APIOps publishes changes |
| APIOps publisher | Git-to-APIM deployment path after approved change |

## Evolution path

Many enterprises start with a centralized APIM instance:

```text
One APIM instance
  APIs grouped by team/domain
  Products grouped by audience/tier
  GitHub CODEOWNERS controls who can change what
```

As they scale, especially on Premium or Premium v2, they may move to a federated workspace model:

```text
One enterprise APIM service
  Workspace: catalog
    APIs, products, subscriptions, named values for catalog team
  Workspace: orders
    APIs, products, subscriptions, named values for orders team
  Platform team
    Global policy, observability, networking, developer portal, governance
```

The strongest enterprise message for this demo is:

> Teams own APIs, the platform owns governance, and products define how consumers get access.
