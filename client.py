# -*- coding: utf-8 -*-
"""
OpenClaw GenPark Market Sniper - Sub-Millisecond On-Chain DEX Liquidity Pool Sniper & MEV Protection
Standard Library only: math, typing.
Calculates CPMM price impact, analytically derives optimal swap sizing for fair-value arbitrage,
and computes MEV sandwich attack risk for private mempool flashbot routing.
"""

import math
from typing import Dict, List, Any

class OpenClawGenParkMarketSniper:
    def __init__(self, default_fee_bps: float = 30.0):
        self.default_fee_bps = default_fee_bps

    def calculate_amm_price_and_impact(self, reserve_in: float, reserve_out: float,
                                       amount_in: float,
                                       fee_bps: float = None) -> Dict[str, Any]:
        """
        Calculates exact Constant Product (x * y = k) swap execution, slippage, and price impact.
        """
        fee = (fee_bps if fee_bps is not None else self.default_fee_bps) / 10000.0
        amount_in_with_fee = amount_in * (1.0 - fee)
        
        # Spot price before swap (Quote per Base, assuming token_in is Base)
        spot_price_before = reserve_out / reserve_in if reserve_in > 0 else 0.0

        # Output amount: dy = (y * dx_net) / (x + dx_net)
        numerator = reserve_out * amount_in_with_fee
        denominator = reserve_in + amount_in_with_fee
        amount_out = numerator / denominator if denominator > 0 else 0.0

        # New reserves
        new_reserve_in = reserve_in + amount_in
        new_reserve_out = reserve_out - amount_out

        # Spot price after swap
        spot_price_after = new_reserve_out / new_reserve_in if new_reserve_in > 0 else 0.0

        # Execution price
        execution_price = amount_out / amount_in if amount_in > 0 else 0.0

        # Price impact percentage
        price_impact_pct = abs(spot_price_after - spot_price_before) / spot_price_before * 100.0 if spot_price_before > 0 else 0.0

        return {
            "amount_in": amount_in,
            "amount_out": round(amount_out, 6),
            "spot_price_before": round(spot_price_before, 6),
            "spot_price_after": round(spot_price_after, 6),
            "effective_execution_price": round(execution_price, 6),
            "price_impact_pct": round(price_impact_pct, 4),
            "pool_k_constant": round(reserve_in * reserve_out, 2)
        }

    def compute_optimal_swap_size(self, reserve_in: float, reserve_out: float,
                                  fair_market_price: float,
                                  fee_bps: float = None,
                                  gas_cost_quote: float = 0.0) -> Dict[str, Any]:
        """
        Analytically solves for optimal input dx* that maximizes net arbitrage profit:
        dx* = (sqrt(x * y * P_fair * gamma) - x) / gamma
        where gamma = 1 - fee
        """
        fee = (fee_bps if fee_bps is not None else self.default_fee_bps) / 10000.0
        gamma = 1.0 - fee

        # Current pool price: P_pool = y / x
        pool_price = reserve_out / reserve_in if reserve_in > 0 else 0.0
        if pool_price <= 0:
            return {"error": "Invalid pool reserves"}

        # Check if arbitrage direction is valid (fair price > pool price)
        term = reserve_in * reserve_out * fair_market_price * gamma
        if term <= 0:
            optimal_dx = 0.0
        else:
            optimal_dx = (math.sqrt(term) - reserve_in) / gamma

        optimal_dx = max(0.0, optimal_dx)

        if optimal_dx > 0.0:
            # Calculate output and profit
            res = self.calculate_amm_price_and_impact(reserve_in, reserve_out, optimal_dx, fee_bps)
            dy = res["amount_out"]
            gross_profit_quote = dy - (optimal_dx * (1.0 / fair_market_price))
            net_profit_quote = gross_profit_quote - gas_cost_quote
            is_profitable = net_profit_quote > 0.0
        else:
            dy = 0.0
            gross_profit_quote = 0.0
            net_profit_quote = -gas_cost_quote
            is_profitable = False

        return {
            "optimal_amount_in": round(optimal_dx, 4),
            "expected_amount_out": round(dy, 4),
            "pool_price_before": round(pool_price, 6),
            "fair_market_price": round(fair_market_price, 6),
            "gross_profit_quote": round(gross_profit_quote, 4),
            "gas_cost_quote": round(gas_cost_quote, 4),
            "net_profit_quote": round(net_profit_quote, 4),
            "is_profitable": is_profitable
        }

    def evaluate_mev_sandwich_risk(self, pool_liquidity_usd: float,
                                   swap_size_usd: float,
                                   slippage_tolerance_pct: float,
                                   mempool_pending_txs: int = 5) -> Dict[str, Any]:
        """
        Evaluates vulnerability to frontrunning / sandwich attacks and generates routing advice.
        """
        pool_liq = max(100.0, pool_liquidity_usd)
        swap_ratio = swap_size_usd / pool_liq

        # Max safe slippage without being an easy MEV sandwich target
        max_safe_slippage_pct = max(0.1, swap_ratio * 150.0)
        
        # Risk index [0, 1]
        raw_risk = (slippage_tolerance_pct / max_safe_slippage_pct) * (1.0 + mempool_pending_txs / 10.0) * 0.4
        risk_score = min(1.0, max(0.0, raw_risk))

        if risk_score >= 0.65:
            verdict = "CRITICAL_SANDWICH_RISK"
            routing = "FLASHBOTS_PRIVATE_RPC_REQUIRED"
        elif risk_score >= 0.35:
            verdict = "MODERATE_SANDWICH_EXPOSURE"
            routing = "MEV_PROTECTED_PUBLIC_BUNDLE"
        else:
            verdict = "LOW_MEV_RISK"
            routing = "STANDARD_PUBLIC_MEMPOOL"

        recommended_slippage_pct = min(slippage_tolerance_pct, max(0.1, max_safe_slippage_pct * 0.6))

        return {
            "swap_size_usd": swap_size_usd,
            "pool_liquidity_usd": pool_liq,
            "swap_to_pool_ratio_pct": round(swap_ratio * 100.0, 3),
            "configured_slippage_pct": slippage_tolerance_pct,
            "max_safe_slippage_pct": round(max_safe_slippage_pct, 3),
            "mev_risk_score": round(risk_score, 3),
            "risk_verdict": verdict,
            "recommended_routing": routing,
            "recommended_tight_slippage_pct": round(recommended_slippage_pct, 2)
        }
