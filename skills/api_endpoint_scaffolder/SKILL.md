---
name: api_endpoint_scaffolder
version: 1.0.0
description: End-to-end routine for scaffolding production-ready API endpoints, schemas, validation, router registration, and tests.
author: kuroLabs-ai
tags: [api, rest, backend, scaffolding, fast-api, express, testing]
---

# API Endpoint Scaffolder Skill Routine

Systematic workflow routine for designing, implementing, and validating production-ready RESTful API endpoints across modern backend frameworks (FastAPI, Express/NestJS, Flask, Go, etc.).

## Overview
This procedure guarantees that every new endpoint follows clean architecture: strict request/response data contracts, status code correctness, input sanitization, error handling, route registration, and automated integration tests.

## Routine Steps:

1. **Contract & Schema Definition**:
   - Determine resource entity, HTTP method (`GET`, `POST`, `PUT`, `PATCH`, `DELETE`), and URL path.
   - Define strict input payload schemas (e.g., Pydantic model, Zod schema, or dataclass) with type validation, constraints, and defaults.
   - Define serialized response models and explicit error response schemas (e.g., 400 Bad Request, 404 Not Found, 409 Conflict).

2. **Integration Test Scaffolding (Test-First Alignment)**:
   - Scaffold test suite in `tests/` covering:
     - Happy path (200 OK / 201 Created) with expected response body structure.
     - Validation error path (422 / 400 Bad Request) on missing or malformed fields.
     - Resource not found path (404) on non-existent identifier lookups.
     - Permission or authentication check (401 / 403) when route is protected.

3. **Controller & Service Layer Implementation**:
   - Implement route handler adhering to dependency injection and single-responsibility principles.
   - Isolate database or external service calls in a dedicated service/repository layer.
   - Ensure proper exception catching so unhandled errors return clean structured JSON responses rather than raw 500 stack traces.

4. **Router Registration & API Documentation**:
   - Register route with the parent router or application blueprint.
   - Add docstrings, tags, query parameter descriptions, and summary annotations for OpenAPI/Swagger generation.
   - Execute test suite to verify all test cases pass cleanly without regressions.
