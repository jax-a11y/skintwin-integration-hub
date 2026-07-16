# Ecosystem Position: skintwin-integration-hub

> This repository is part of the [SkinTwin-AI ecosystem](https://github.com/jax-a11y/skintwin-ecosystem-design). Its machine-readable manifest lives at [`.skintwin/manifest.json`](.skintwin/manifest.json); the ecosystem-wide source of truth is `registry/ecosystem.json` in the hub repo.

**Layer:** integration · **Role:** integration-gateway

This repo is the Flask integration layer that connects the Amazing Salon App platform to Wix Appointment Bookings, OpenCart, and the Shopify B2B ecosystem. It exposes a unified API gateway under `/api/integrations/*`, maps platform data into canonical `Unified*` models, and routes incoming platform webhooks into unified events for cross-platform workflows. Within the ecosystem it occupies the integration layer, so downstream services call one gateway instead of three vendor APIs.

## Provides

*   `integration-api` — Unified gateway to Wix/OpenCart/Shopify B2B: health, sync (appointments/clients/products), B2B companies. REST, served under `/api/integrations/*`.

## Consumes

Nothing — as the integration gateway, this repo talks outward to third-party platforms (Wix, OpenCart, Shopify) rather than consuming other ecosystem services.

## Events

Payload schemas for each topic live at `contracts/events/<topic>.schema.json` in the hub repo.

| Topic | Direction |
| --- | --- |
| `order.created` | publishes |
| `order.paid` | publishes |
| `product.updated` | publishes |
| `appointment.created` | publishes |
| `appointment.updated` | publishes |
| `inventory.updated` | publishes |
| `user.created` | subscribes |

## CI

This repo runs its own workflow, `ci-build.yml` (ruff/flake8/mypy, pytest, DB checks), and does not currently call the shared templates. Reusable `workflow_call` CI templates for the ecosystem are documented in the hub repo's `ci/README.md`.
