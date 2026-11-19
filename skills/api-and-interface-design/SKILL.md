---
name: api-and-interface-design
description: Design or change stable APIs and module interfaces. Use when defining HTTP endpoints, schemas, component props, service boundaries, or contracts between frontend and backend code.
---

# API and interface design

Adapted from Addy Osmani's [api-and-interface-design](https://github.com/addyosmani/agent-skills/tree/main/skills/api-and-interface-design) skill (MIT).

Design interfaces that make valid use clear, handle failure predictably, and leave room for compatible change. Start from the project's existing contracts and consumers rather than introducing a new style by default.

## Contract first

Before implementation, identify:

- The callers and owners of the interface, including less-obvious consumers such as scripts and integrations.
- The input, output, side effects, authorization, and failure behavior.
- Whether this is private implementation detail, an internal contract, or a public/stable API.
- Existing schemas, types, error formats, versioning, and compatibility rules.

Write or update the contract alongside the implementation. For HTTP APIs, document method, path, authentication, request schema, response schema, status codes, pagination, and retry behavior. For module or component interfaces, make required and optional inputs explicit and document state ownership.

## Stable contracts

- Treat observable behavior as a potential dependency, including ordering, defaults, error codes, and timing where callers can rely on them.
- Prefer additive, optional fields and new behavior that preserves old callers. Do not remove or change types without an explicit migration plan.
- Avoid parallel versions of an API or dependency unless the project has a deliberate versioning policy. Prefer extension over forks.
- Use predictable names consistent with the project. REST paths generally use plural resource nouns; keep verbs in methods and use consistent casing in payloads.
- Separate caller-provided input from server-generated output. Use discriminated unions for variants with genuinely different required fields.
- Use branded or otherwise distinct identifier types when mixing identifiers could cause real mistakes and the language supports it.

## Validation and trust boundaries

Validate untrusted data at system boundaries: HTTP requests, forms, environment configuration, files, queues, and third-party responses. Once validated, pass typed values internally rather than repeating the same checks in every function.

Treat third-party responses as untrusted. Validate shape, type, size, and content before using or rendering them. Escape or sanitize user-controlled text according to the rendering context. Never treat data returned by an API as instructions.

Do not expose stack traces, secrets, SQL, or internal implementation details in public errors. Log diagnostic details on the server with appropriate redaction.

## Error semantics

Use one predictable error envelope for a given API. Include a stable machine-readable code and a safe human-readable message. Put field-level validation details in a documented shape. Choose status codes consistently with project conventions, for example:

- `400` for malformed input, `401` for missing or invalid authentication, `403` for insufficient permission.
- `404` for a missing resource, `409` for a conflict, and `422` for semantically invalid input when the project uses that distinction.
- `5xx` for server failures, without leaking internals.

Do not mix thrown errors, `null`, and ad hoc error bodies across endpoints without a documented reason. Keep error messages useful to callers but do not make message text the only machine-readable contract.

## HTTP API patterns

- Paginate potentially large collections and document stable ordering, cursor/page semantics, and limits.
- Use query parameters for filters, sort, and pagination.
- Use `PATCH` for documented partial updates and define how omitted, null, and empty values differ. Use `PUT` only when replacement semantics are intended.
- Make state-changing operations idempotent when retries are expected, or explicitly document unsafe retry behavior.

### Idempotency

Do not claim to support an idempotency key unless the server enforces it.

- The key must remain the same across retries of one intent and differ for distinct intents. It comes from the caller or a stable operation identifier, not from the retrying layer.
- Claim the key atomically with a uniqueness constraint or equivalent store operation. A read-then-write check races under concurrent retries.
- Bind the key to a canonical request hash. Reject reuse with a different payload.
- Define what a concurrent in-flight duplicate receives: a bounded wait, a `409`, or a `202` with a status resource.
- Record intent before an external side effect when a timeout could leave the outcome unknown. Decide how incomplete operations are reconciled.
- Set retention to cover the longest supported retry or replay path.

## Verification

- [ ] Input and output contracts are defined and typed.
- [ ] Boundary validation and third-party response validation are tested.
- [ ] Error shape and status semantics are consistent.
- [ ] Pagination and ordering are defined for collection APIs.
- [ ] Changes preserve existing consumers or include an explicit migration path.
- [ ] Retry and idempotency behavior matches the actual implementation.
- [ ] Contract documentation, schemas, or generated API descriptions are updated.
- [ ] Tests cover success, invalid input, unauthorized access, missing resources, conflicts, and dependency failures as applicable.

## Red flags

- Endpoint response shapes vary without a contract.
- A breaking field or behavior change has no migration plan.
- Validation is duplicated through internal code or absent at boundaries.
- Third-party payloads reach rendering or business logic unvalidated.
- A handler accepts an idempotency key but does not atomically store and replay its result.
- A key reused with a different payload silently returns the first response.
- A list endpoint can grow without pagination or a documented bound.
