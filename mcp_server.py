# -*- coding: utf-8 -*-
import sys, json
from client import OpenClawGenParkMarketSniper

client = OpenClawGenParkMarketSniper()

TOOLS = [
    {
        "name": "calculate_amm_price_and_impact",
        "description": "Calculates CPMM output amount, execution price, and price impact percentage.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "reserve_in": {"type": "number"},
                "reserve_out": {"type": "number"},
                "amount_in": {"type": "number"},
                "fee_bps": {"type": "number"}
            },
            "required": ["reserve_in", "reserve_out", "amount_in"]
        }
    },
    {
        "name": "compute_optimal_swap_size",
        "description": "Analytically solves for optimal swap size dx* that maximizes net arbitrage profit.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "reserve_in": {"type": "number"},
                "reserve_out": {"type": "number"},
                "fair_market_price": {"type": "number"},
                "fee_bps": {"type": "number"},
                "gas_cost_quote": {"type": "number"}
            },
            "required": ["reserve_in", "reserve_out", "fair_market_price"]
        }
    },
    {
        "name": "evaluate_mev_sandwich_risk",
        "description": "Evaluates sandwich attack risk and recommends private Flashbots RPC vs public mempool.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "pool_liquidity_usd": {"type": "number"},
                "swap_size_usd": {"type": "number"},
                "slippage_tolerance_pct": {"type": "number"},
                "mempool_pending_txs": {"type": "integer"}
            },
            "required": ["pool_liquidity_usd", "swap_size_usd", "slippage_tolerance_pct"]
        }
    }
]

def handle_request(req):
    method = req.get("method")
    rid = req.get("id")
    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": rid, "result": {"tools": TOOLS}}
    elif method == "tools/call":
        params = req.get("params", {})
        tname = params.get("name")
        args = params.get("arguments", {})
        if tname == "calculate_amm_price_and_impact":
            res = client.calculate_amm_price_and_impact(args["reserve_in"], args["reserve_out"], args["amount_in"], args.get("fee_bps"))
            return {"jsonrpc": "2.0", "id": rid, "result": {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}}
        elif tname == "compute_optimal_swap_size":
            res = client.compute_optimal_swap_size(args["reserve_in"], args["reserve_out"], args["fair_market_price"], args.get("fee_bps"), args.get("gas_cost_quote", 0.0))
            return {"jsonrpc": "2.0", "id": rid, "result": {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}}
        elif tname == "evaluate_mev_sandwich_risk":
            res = client.evaluate_mev_sandwich_risk(args["pool_liquidity_usd"], args["swap_size_usd"], args["slippage_tolerance_pct"], args.get("mempool_pending_txs", 5))
            return {"jsonrpc": "2.0", "id": rid, "result": {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}}
        return {"jsonrpc": "2.0", "id": rid, "error": {"code": -32601, "message": "Method not found"}}
    return {"jsonrpc": "2.0", "id": rid, "error": {"code": -32600, "message": "Invalid Request"}}

def main():
    for line in sys.stdin:
        if not line.strip(): continue
        try:
            req = json.loads(line)
            resp = handle_request(req)
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()
        except Exception as e:
            sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": str(e)}}) + "\n")
            sys.stdout.flush()

if __name__ == "__main__":
    main()
