---
name: openclaw-genpark-market-sniper
description: OpenClaw GenPark Market Sniper - Sub-millisecond on-chain DEX liquidity pool sniper with CPMM impact, analytical optimal sizing, and MEV sandwich protection.
category: Service
version: 1.0.0
license: MIT
tools:
  - calculate_amm_price_and_impact
  - compute_optimal_swap_size
  - evaluate_mev_sandwich_risk
---

# Openclaw Genpark Market Sniper

## Overview & Agent Behavioral Directives
You are an autonomous agent specialized in **Openclaw Genpark Market Sniper**.
Your primary directive is to execute: OpenClaw GenPark Market Sniper - Sub-millisecond on-chain DEX liquidity pool sniper with CPMM impact, analytical optimal sizing, and MEV sandwich protection.
Always ensure mathematical precision, parameter validation, and deterministic outputs.

## When to Activate This Skill
- Activate when an agent workflow or user instruction requires:
- `calculate_amm_price_and_impact`
- `compute_optimal_swap_size`
- `evaluate_mev_sandwich_risk`
- Activate when operating in zero-dependency environments requiring pure Python standard library execution.

## How to Execute

### Option 1: Direct Python Execution (Zero-Dependency)
```python
from client import *

# Client operates purely on standard Python library:
# Initialized and ready for direct function invocation.
```

### Option 2: FastMCP Tool Calling
Tools registered in `mcp_server.py`:
- `calculate_amm_price_and_impact`
- `compute_optimal_swap_size`
- `evaluate_mev_sandwich_risk`

## Core Mathematical & Algorithmic Guardrails
- **Zero-Dependency Policy**: 100% Python standard library only (`math`, `heapq`, `hashlib`, `urllib`, `collections`, `itertools`, `typing`).
- **Zero-Mock Policy**: Pure deterministic algorithms with full validation and error bounds.
