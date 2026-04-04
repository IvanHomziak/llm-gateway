# User Story 1 – Base Service Skeleton and Architecture

## Goal
Establish a clean, minimal, and extensible foundation for `llm-gateway` so future endpoint work (`/health`, `/chat`, `/summarize`) follows strict layer boundaries: **router -> service -> provider**.

This story is about defining and documenting the service skeleton and package responsibilities, not implementing business behavior.

## Scope
### In scope for User Story 1
- Define canonical package/module boundaries for API, services, providers, schemas, and core infrastructure.
- Define dependency direction and interaction contracts between layers.
- Define where future endpoint, provider, and observability code should live.
- Document file-level responsibilities and TODO tasks to guide implementation.
- Align structure with repository architecture rules from `AGENTS.md`.

### Out of scope for User Story 1
- Implementing endpoint logic for `/api/v1/health`, `/api/v1/chat`, `/api/v1/summarize`.
- Implementing provider SDK calls (OpenAI or any vendor).
- Implementing service orchestration/business logic.
- Implementing production-ready validation, retry strategies, tracing exporters, or logging sinks.
- Adding dependencies, changing runtime behavior, or shipping complete test coverage for business flows.

## Target project structure
The repository already contains a partial skeleton under `app/api/*`, but key bootstrap and test modules are still absent or empty. The target structure for this story should be:

```text
app/
  main.py                          # FastAPI app factory/bootstrap; router registration
  api/
    dependencies.py                # Dependency providers for router layer (service wiring)
    routers/
      health.py                    # GET /api/v1/health route declarations
      chat.py                      # POST /api/v1/chat route declarations
      summarize.py                 # POST /api/v1/summarize route declarations
  schemas/
    common.py                      # Shared contract primitives (metadata, correlation IDs)
    health.py                      # Health request/response contracts
    chat.py                        # Chat request/response contracts
    summarize.py                   # Summarize request/response contracts
    error.py                       # Canonical API error contracts
  services/
    health_service.py              # Health use-case orchestration
    chat_service.py                # Chat use-case orchestration
    summarize_service.py           # Summarize use-case orchestration
  providers/
    base.py                        # Provider protocol/ABC for chat & summarize operations
    openai_provider.py             # Vendor-specific implementation placeholder
  core/
    config.py                      # Typed settings from environment variables
    exceptions.py                  # Domain/app exception taxonomy and mapping helpers
    logging.py                     # Structured logger setup + correlation propagation hooks
    tracing.py                     # Tracing/span helper abstraction

tests/
  unit/
    routers/                       # Router tests (contract/HTTP behavior with mocked services)
    services/                      # Service tests (orchestration with mocked providers)
    providers/                     # Provider adapter tests (no network by default)
  integration/
    test_app_bootstrap.py          # App creation and router registration checks
```

### Notes on current-vs-target placement
- Current repository places `core`, `providers`, `schemas`, and `services` under `app/api/*`.
- For clean architecture clarity, those modules should conceptually belong at `app/core`, `app/providers`, `app/schemas`, `app/services` (or documented as intentionally nested if team prefers `app/api/*`).
- If physical moves are deferred, equivalent logical boundaries must still be enforced.

## Classes / modules to introduce
> The list below describes responsibilities; it is intentionally implementation-free.

### `app/main.py`
- **Responsibility:** Create FastAPI application, register middlewares (future), include versioned routers.
- **Why needed:** Central app bootstrap keeps transport concerns in one entry point and avoids ad-hoc initialization.

### `app/api/routers/health.py`
- **Responsibility:** Define `/api/v1/health` route, request/response model bindings, HTTP status mappings.
- **Why needed:** Isolates HTTP contract for health checks from business/provider logic.

### `app/api/routers/chat.py`
- **Responsibility:** Define `/api/v1/chat` route surface; validate inputs via schemas; invoke service.
- **Why needed:** Keeps endpoint protocol stable while service/provider internals evolve.

### `app/api/routers/summarize.py`
- **Responsibility:** Define `/api/v1/summarize` route surface and response model mapping.
- **Why needed:** Preserves thin-router discipline and clear endpoint ownership.

### `app/api/dependencies.py`
- **Responsibility:** Provide dependency wiring functions (e.g., service factories) for routers.
- **Why needed:** Prevents manual object construction inside handlers and centralizes composition.

### `app/schemas/*` (or existing `app/api/schemas/*` if retained)
- **Responsibility:** Hold Pydantic request/response contracts and canonical error payload models.
- **Why needed:** Protects API contract stability, validation consistency, and non-leakage of provider payloads.

### `app/services/chat_service.py`, `app/services/summarize_service.py`, `app/services/health_service.py`
- **Responsibility:** Orchestrate use cases, call provider abstractions, normalize outputs/errors.
- **Why needed:** Keeps business workflow out of routers and vendor SDK code.

### `app/providers/base.py`
- **Responsibility:** Define provider interface/ABC/protocol for required LLM operations.
- **Why needed:** Enables dependency inversion and testability via mocked provider contracts.

### `app/providers/openai_provider.py`
- **Responsibility:** Implement vendor-specific adapter adhering to `providers.base` contracts.
- **Why needed:** Encapsulates SDK details, retries/timeouts, and response translation.

### `app/core/config.py`
- **Responsibility:** Typed settings loaded from environment; provider/runtime config objects.
- **Why needed:** Prevents hardcoded secrets and centralizes operational controls.

### `app/core/exceptions.py`
- **Responsibility:** Application exception hierarchy and mapping rules to canonical API errors.
- **Why needed:** Consistent error semantics across routers/services/providers.

### `app/core/logging.py`
- **Responsibility:** Structured logging setup and safe log-field policy (no keys/full prompts).
- **Why needed:** Supports operability and security while preserving privacy controls.

### `app/core/tracing.py`
- **Responsibility:** Span helpers/instrumentation points for request->service->provider flow.
- **Why needed:** Enables traceability and latency diagnostics across layers.

### `tests/*`
- **Responsibility:** Verify layering and contracts with unit/integration checks.
- **Why needed:** Enforces architecture over time and catches boundary regressions.

## Layering rules
### Routers may
- Parse HTTP request metadata and path/body parameters.
- Bind `response_model` and translate known exceptions to HTTP responses.
- Call service interfaces obtained via dependency injection.

### Routers must not
- Call provider SDKs directly.
- Contain orchestration/business decisions.
- Perform retry/timeouts or vendor payload transformations.

### Services may
- Orchestrate use-case steps and policy decisions.
- Coordinate provider calls through abstractions.
- Normalize provider/domain errors for API layer consumption.

### Services must not
- Depend on FastAPI request/response primitives.
- Import vendor SDK-specific code directly (use provider abstraction).
- Return raw provider payloads without contract mapping.

### Providers may
- Execute vendor-specific HTTP/SDK calls.
- Apply provider-level retries/timeouts (from config).
- Translate vendor responses/errors into internal provider result objects.

### Providers must not
- Know HTTP router concerns (status codes, request objects).
- Implement endpoint-level orchestration or cross-use-case policy.
- Leak secrets/sensitive prompts in logs.

## Dependency flow
Intended request lifecycle:

1. **Request enters router** (`/api/v1/...`).
2. Router validates input against schema contracts and extracts HTTP context.
3. Router calls a **service** interface from dependency wiring.
4. Service executes use-case orchestration and calls a **provider abstraction**.
5. Provider implementation talks to vendor SDK/API and returns normalized result.
6. Service maps normalized result to domain/API response DTO.
7. Router returns response model to client (canonical schema).

Directional dependency rule:
- `api/routers -> services -> providers`
- `schemas` shared for contracts (primarily router/service boundaries).
- `core` consumed by services/providers (and selectively by app bootstrap/router exception handlers).
- No upward dependency from providers to routers.

## Missing items in current repository
Based on current tree and file contents:

- `app/main.py` does not exist (no explicit app bootstrap entry point).
- All existing Python modules are empty placeholders (0-byte files), so no responsibilities are encoded yet.
- Layer placement currently groups everything under `app/api/*`; logical boundaries are present only by folder names, not implementation.
- No health service module exists (`health_service.py` missing).
- No test modules beyond empty `tests/__init__.py`.
- No documented router registration, dependency wiring, error mapping, or observability hooks.
- No declared tooling config files (lint/type/test config) were found.

## TODO list
### TODO: package structure and bootstrapping
- [ ] Create `app/main.py` with app bootstrap skeleton and router inclusion plan.
- [ ] Decide final module placement (`app/api/*` nested vs flattened `app/{services,providers,...}`) and document the decision.
- [ ] Add package `__init__.py` files for any new directories required by the chosen layout.

### TODO: router layer
- [ ] Define route modules for health/chat/summarize with explicit `response_model` placeholders.
- [ ] Add canonical exception-to-HTTP mapping hooks (no business logic).
- [ ] Ensure each router consumes services through dependency providers only.

### TODO: service layer
- [ ] Add `health_service.py`, `chat_service.py`, `summarize_service.py` skeleton interfaces/classes.
- [ ] Define service input/output DTO expectations tied to schema/domain models.
- [ ] Document orchestration boundaries and error normalization rules.

### TODO: provider layer
- [ ] Define provider base protocol in `providers/base.py` for chat/summarize capabilities.
- [ ] Add vendor adapter placeholder module(s), starting with OpenAI.
- [ ] Document timeout/retry ownership and provider error translation expectations.

### TODO: schema/contracts layer
- [ ] Define request/response schema modules for health/chat/summarize.
- [ ] Define reusable common metadata models and canonical error schema.
- [ ] Document anti-leak rule: API responses must not expose raw vendor payloads.

### TODO: core infrastructure
- [ ] Define typed environment settings in `core/config.py`.
- [ ] Define exception taxonomy in `core/exceptions.py`.
- [ ] Define structured logging policy and correlation ID propagation in `core/logging.py`.
- [ ] Define tracing spans for router/service/provider boundaries in `core/tracing.py`.

### TODO: tests and quality gates
- [ ] Create unit test skeletons for routers with mocked services.
- [ ] Create unit test skeletons for services with mocked providers.
- [ ] Add app bootstrap/integration smoke tests for router registration.
- [ ] Add CI-ready command list for tests/lint/format once tooling is selected.

## Acceptance criteria interpretation
User Story 1 should be considered complete (architecturally) when:

- A clear package skeleton exists for router/service/provider/schemas/core layers.
- Module responsibilities and ownership boundaries are explicitly documented in-repo.
- Dependency direction is enforceable by design (`router -> service -> provider`).
- API contracts are planned via dedicated schema modules and canonical errors.
- Configuration, logging, tracing, and exception modules are planned as separate concerns.
- A practical TODO/test plan exists for implementing future stories without violating architecture.

Not required for completion of Story 1:
- Working endpoint behavior.
- Working provider integration.
- End-to-end business functionality.

## Risks / design notes
Key failure modes to avoid in future implementation:

- **Fat routers:** handlers accumulating orchestration and branching logic.
- **Direct SDK calls from routers:** bypasses service abstraction and harms testability.
- **Layer leakage:** business decisions inside providers or HTTP concerns inside services.
- **Monolithic module growth:** putting bootstrap, routers, services, and provider adapters in one file.
- **Raw vendor payload leakage:** exposing provider response shape directly to external API clients.
- **Observability overexposure:** logging secrets, prompts, or full model outputs.
- **Retry duplication:** retries in both service and provider layers causing compounded latency.

Recommended guardrails:
- Maintain strict constructor-based dependency injection.
- Mock provider abstractions in service tests.
- Keep schema evolution explicit and version-aware under `/api/v1` routing.
