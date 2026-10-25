# Recon Desk — build guide

## What this is
Multi-tenant reconciliation app. Finds mismatches between a company's internal
payment ledger and Stripe, diagnoses each with an LLM, and holds every proposed
fix for human approval. Portfolio project; lane = AI product engineer.

## Stack
- engine/ — Python reconciliation engine (deterministic match first, LLM only for ambiguous cases)
- apps/web/ — TypeScript / Next.js (later)
- infra/ — Terraform on AWS (later)
- Postgres for data.

## Conventions
- Decisions live in docs/adr/, one numbered file each.
- Write the first instance of a pattern by hand; let agents repeat it; review every diff.

## Hard rule
No proposed fix ever auto-executes. The human approval gate is the product.
