# Vireo Audio — AI Diagnostics Prompt Documentation

This directory contains versioned prompts for the qualitative ticket diagnosis layer.

## Version History

### `ticket_diagnosis_v1.txt` (Active)
- **Role:** Quality Assurance and Support Operations Auditor.
- **Goal:** Classify observable operational evidence to answer: *"Why does this interaction appear problematic or dissatisfied?"*
- **Key Categories:**
  - `primary_root_cause`: `agent_handling`, `product_or_hardware`, `policy_or_process`, `queue_or_case_mix`, `customer_or_external`, `unclear`.
  - `agent_handling_signal`: `none`, `weak`, `moderate`, `strong`.
  - `resolution_quality`: `appropriate`, `partially_appropriate`, `inappropriate`, `unclear`.
  - `customer_sentiment`: `negative`, `neutral`, `positive`, `unclear`.
  - `policy_signal`: `none`, `possible`, `clear`.
  - `evidence_quality`: `sufficient`, `limited`, `insufficient`.
  - `confidence`: `low`, `medium`, `high`.
  - `evidence`: Short factual citation strictly from text.
- **Constraints:**
  - No inference beyond supplied text.
  - No fabrication of product defect or policy violation without direct textual support.
  - Failed IVR transcripts must be tagged with `evidence_quality: "insufficient"` and `confidence: "low"`.
  - Strict JSON output matching schema; non-conforming responses are rejected.

## Data Minimization & Privacy Rules
Prompts are stripped of all PII:
- No customer names, phone numbers, or addresses.
- No city or geographic data.
- Ticket ID is used strictly as an internal referential key.
