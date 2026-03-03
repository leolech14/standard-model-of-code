"""Trading tools: positions, thresholds, auto-trading, market state."""

from tool_registry import ToolSpec, registry

TOOLS = [
    ToolSpec(
        name="get_trading_status",
        description="Get current Binance trading status: positions, PnL, zones, alerts.",
        parameters={"type": "object", "properties": {}},
        method="GET",
        path="/api/trading/current",
        max_chars=3000,
        tags=["trading"],
    ),
    ToolSpec(
        name="manage_thresholds",
        description="Get current trading zone thresholds configuration.",
        parameters={"type": "object", "properties": {}},
        method="GET",
        path="/api/thresholds",
        tags=["trading"],
    ),
    ToolSpec(
        name="best_trades",
        description="Get the best trading opportunities ranked by confidence score. Scans all tracked symbols across timeframes. Use when Leo asks 'best trades?', 'what should I trade?', 'melhores oportunidades', 'best scalps?', 'top setups', etc.",
        parameters={
            "type": "object",
            "properties": {
                "tf": {
                    "type": "string",
                    "enum": ["1m", "5m", "15m", "1h", "4h"],
                    "description": "Timeframe",
                },
                "direction": {
                    "type": "string",
                    "enum": ["best", "long", "short"],
                    "description": "Direction filter",
                },
            },
        },
        method="GET",
        path="/api/trading/ranking",
        arg_transform=lambda a: {
            **{k: v for k, v in a.items() if v},
            "limit": "10",
        },
        max_chars=3000,
        tags=["trading"],
    ),
    ToolSpec(
        name="toggle_auto_trading",
        description="Enable, disable, or check status of the autonomous auto-entry trading system. Use when Leo says 'enable auto trading', 'disable auto entry', 'auto trading status', 'ligar trading automatico', 'desligar auto entry'. Can also set margin percentage, max positions, and entry size.",
        parameters={
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["enable", "disable", "go_live", "advisory", "status"],
                    "description": "Action to perform",
                },
                "max_mr": {"type": "number", "description": "Max margin ratio"},
                "size_pct": {"type": "number", "description": "Position size %"},
                "max_positions": {"type": "integer", "description": "Max open positions"},
            },
            "required": ["action"],
        },
        method="POST",
        path="/api/trading/auto-entry/toggle",
        timeout=20,
        max_chars=3000,
        tags=["trading"],
    ),
    ToolSpec(
        name="check_auto_trading",
        description="Check status of the autonomous auto-entry trading system. Shows if enabled, advisory/live mode, margin limits, max positions.",
        parameters={"type": "object", "properties": {}},
        method="GET",
        path="/api/trading/auto-entry",
        source="elevenlabs",
        tags=["trading"],
    ),
    ToolSpec(
        name="market_state",
        description="Get current market state: day type (WAVE_UP, WAVE_DOWN, CHOP, ROTATION, BTC_ONLY), breadth, dispersion, BTC sync, top movers. Use when Leo asks 'how is the market?', 'market state', 'day type', 'como esta o mercado?', 'bull or bear?', 'market conditions'.",
        parameters={"type": "object", "properties": {}},
        method="GET",
        path="/api/trading/market-state",
        max_chars=3000,
        tags=["trading"],
    ),
    ToolSpec(
        name="cashout_brl",
        description="Withdraw BRL from Binance to PicPay via Pix. Transfers USDT from futures to spot, converts to BRL, then withdraws via Pix. Requires confirmation before executing. Use when Leo says 'saca', 'withdraw reais', 'manda pra PicPay', 'cashout BRL', etc.",
        parameters={
            "type": "object",
            "properties": {
                "amount_brl": {"type": "number", "description": "Amount in BRL"},
                "pix_key": {"type": "string", "description": "Pix key (optional)"},
            },
            "required": ["amount_brl"],
        },
        method="POST",
        path="/api/voice/finance/binance/cashout-brl",
        arg_transform=lambda a: {
            "amount_brl": a.get("amount_brl"),
            "pix_key": a.get("pix_key"),
            "requested_by": "voice",
        },
        tags=["trading", "finance"],
    ),
    ToolSpec(
        name="binance_withdraw",
        description="Prepare/execute Binance withdraw. payload can be JSON string.",
        parameters={"type": "object", "properties": {}},
        method="POST",
        path="/api/voice/finance/binance/withdraw",
        source="elevenlabs",
        tags=["trading", "finance"],
    ),
]

registry.register_many(TOOLS)
