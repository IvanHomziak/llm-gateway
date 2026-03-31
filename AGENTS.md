# AGENTS.md

## Architecture rules
- Keep application layering as: **router -> service -> provider**.
- Routers must stay thin and only handle HTTP concerns.
- Do not call provider SDKs directly from routers.
- Keep orchestration in services and vendor-specific logic in providers.

## API contract rules
- Use Pydantic models for all request and response contracts.
- Use `response_model` on FastAPI endpoints.
- Expose canonical error responses.
- Do not leak raw provider payloads from API responses.

## Configuration rules
- Load configuration from environment variables.
- Never hardcode secrets.
- Prefer typed settings.

## Reliability rules
- Configure timeouts and retries in provider/config layers, never in routers.
- Avoid duplicated retry loops across layers.

## Observability rules
- Add structured logs for the request lifecycle.
- Include correlation IDs in logs/traces.
- Add basic tracing spans for request, service, and provider calls.
- Never log API keys.
- Never log full sensitive request payloads.
- Avoid logging raw prompts or full model outputs in production paths.

## Testing rules
- Add or update tests for every changed behavior.
- Include at least happy-path tests and key negative tests.
- Prefer mocking provider abstractions instead of coupling tests to router internals.

## Verification
- Run the repository test suite.
- Run lint/format checks if configured.
- Summarize assumptions, limitations, and remaining gaps.

## Review guidelines
- Flag layering violations.
- Flag missing validation.
- Flag missing tests for changed behavior.
- Flag timeout/retry mistakes.
- Flag sensitive logging or secret leakage.
- Flag raw provider payload leakage.
