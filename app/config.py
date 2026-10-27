"""Template configuration: env-driven, Base mainnet, one payTo.

Prices are integer USDC base units (1 USDC = 1_000_000), the same
convention the x402 challenges carry — never floats near money.
"""

from __future__ import annotations

import os

USDC_ASSET = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"  # USDC on Base

# Route prices in USDC base units.
PRICE_UNITS: dict[str, int] = {
    "/v1/word-count": 10_000,       # $0.01
    "/v1/pack": 1_000_000,          # $1.00 — 250 prepaid credits
}

PACK_CREDITS = 250
PACK_EXPIRY_DAYS = 90


class Settings:
    def __init__(self) -> None:
        self.service_name = os.environ.get("STALL_NAME", "my-stall")
        self.pay_to = os.environ.get("X402_PAY_TO", "")
        self.network = os.environ.get("X402_NETWORK", "eip155:8453")
        self.facilitator_url = os.environ.get(
            "X402_FACILITATOR_URL", "https://facilitator.ultravioletadao.xyz/"
        )
        self.db_path = os.environ.get("STALL_DB_PATH", "stall.db")


settings = Settings()


def units_to_price(units: int) -> str:
    return f"${units / 1_000_000:.6f}".rstrip("0").rstrip(".")
