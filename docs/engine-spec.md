# ADR-0001: The reconciliation agent is Recon Desk's engine

Date: 2026-10-25
Status: Accepted

## Context
First pass: each year, SAWA (scholastic art and writing awards) manages regional payments via Stripe Connect. we own the "parent" account, regional affiliates own the child accounts. Each region accepts Stripe payments, and we have a set split (TBD) of fees from our backend after Stripe takes its cut; some regions take this split themselves, others are reconciled, which means they refuse to set up a child acct and request that SAWA manages all the $ in their region and pays them a lump sum at the end. This repository needs to look at our reports, Stripe reports and ensure that payments we received and payments we send to affiliates are accurate. 

## Decision
A 'payments agent' should run the rule over source material:
a. Stripe reports
b. Portal (our system) reports

1. Match stripe payment ids (SPI) to our reports' SPIs.
2. Ensure that the $ collected in Stripe matches the # of txns per region less Stripe fees.
3. List all discrepancies (wiere 1 or 2 are off between records).
4. Having completed 1-3, calculate and propose the $ owed to region, justifying with evidentiary reports and a summary of works paid via Stripe. 

## Consequences
<3-4 bullets>

## CLAUDE DRAFT
# Reconciliation engine — what it computes

## Domain (synthetic, modeled on SAWA Stripe Connect)
Parent account owns the relationship; regions are child accounts. Each region
takes Stripe payments; a fee split (TBD) returns to the parent after Stripe's cut.
Self-serve regions keep their split; "reconciled" regions let the parent hold all
funds and get paid a lump sum at period end.

## Inputs
- Stripe reports
- Portal (our-system) reports

## Rules
1. Match Stripe payment IDs (SPI) between Stripe and portal reports.
2. Verify dollars collected in Stripe == per-region txn count less Stripe fees.
3. List every discrepancy where (1) or (2) disagree.
4. Propose dollars owed per region, with evidentiary reports + a summary of works paid.
