# -*- coding: utf-8 -*-
from client import OpenClawGenParkMarketSniper

sniper = OpenClawGenParkMarketSniper()

# 1. CPMM Swap & Price Impact
swap = sniper.calculate_amm_price_and_impact(reserve_in=100000.0, reserve_out=250000.0, amount_in=5000.0, fee_bps=30)
print("CPMM Swap Simulation:")
print(f"  Input: 5000 -> Output: {swap['amount_out']}, Impact: {swap['price_impact_pct']}%")

# 2. Optimal Swap Sizing
# Suppose fair price is 2.80 Quote/Base (Pool price is 2.50)
opt = sniper.compute_optimal_swap_size(reserve_in=100000.0, reserve_out=250000.0, fair_market_price=2.80, fee_bps=30, gas_cost_quote=15.0)
print("\nOptimal Arbitrage Size:")
print(f"  Optimal dx*: {opt['optimal_amount_in']}, Expected Net Profit: ${opt['net_profit_quote']}")

# 3. MEV Sandwich Risk Evaluation
risk = sniper.evaluate_mev_sandwich_risk(pool_liquidity_usd=500000.0, swap_size_usd=25000.0, slippage_tolerance_pct=1.5, mempool_pending_txs=8)
print("\nMEV Sandwich Audit:")
print(f"  Verdict: {risk['risk_verdict']} (Score: {risk['mev_risk_score']}) -> {risk['recommended_routing']}")
