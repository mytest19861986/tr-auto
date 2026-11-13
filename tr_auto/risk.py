"""Owner-approved paper risk invariants; no order submission functions."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from enum import Enum


MAX_NEW_TRADE_NOTIONAL_USD = Decimal("30")
MAX_CONCURRENT_POSITIONS_TOTAL = 4
EVALUATION_CALENDAR_DAYS = 10


class Market(str, Enum):
    STOCK = "stock"
    CRYPTO_SPOT = "crypto_spot"


class Direction(str, Enum):
    LONG = "long"
    SHORT = "short"


@dataclass(frozen=True)
class RiskCheck:
    approved: bool
    reason: str


def check_new_entry(
    *,
    notional_usd: Decimal | str,
    open_positions_total: int,
    reserved_entry_slots_total: int,
    market: Market,
    direction: Direction,
    stock_short_eligible: bool = False,
    stock_short_whole_share: bool = False,
) -> RiskCheck:
    """Conservative preflight. Execution adapter must also enforce broker state.

    Do not use a balance, leverage, rounding or assumed future execution price
    to override the 30-USD notional limit.
    """
    try:
        notional = Decimal(str(notional_usd))
    except (InvalidOperation, ValueError):
        return RiskCheck(False, "INVALID_NOTIONAL")
    if not notional.is_finite() or not (Decimal("0") < notional <= MAX_NEW_TRADE_NOTIONAL_USD):
        return RiskCheck(False, "NOTIONAL_OUT_OF_RANGE")
    if open_positions_total < 0 or reserved_entry_slots_total < 0:
        return RiskCheck(False, "INVALID_SLOT_COUNT")
    if open_positions_total + reserved_entry_slots_total >= MAX_CONCURRENT_POSITIONS_TOTAL:
        return RiskCheck(False, "MAX_CONCURRENT_POSITIONS")
    if market == Market.CRYPTO_SPOT and direction == Direction.SHORT:
        return RiskCheck(False, "CRYPTO_SPOT_SHORT_UNSUPPORTED")
    if market == Market.STOCK and direction == Direction.SHORT:
        if not stock_short_eligible or not stock_short_whole_share:
            return RiskCheck(False, "STOCK_SHORT_NOT_ELIGIBLE")
    if not isinstance(market, Market) or not isinstance(direction, Direction):
        return RiskCheck(False, "INVALID_MARKET_OR_DIRECTION")
    return RiskCheck(True, "PREFLIGHT_PASSED_NOT_AN_ORDER_AUTHORIZATION")
