import unittest
from decimal import Decimal

from tr_auto.risk import (
    EVALUATION_CALENDAR_DAYS,
    MAX_CONCURRENT_POSITIONS_TOTAL,
    MAX_NEW_TRADE_NOTIONAL_USD,
    Direction,
    Market,
    check_new_entry,
)


class PaperRiskTests(unittest.TestCase):
    def test_manager_limits(self):
        self.assertEqual(MAX_NEW_TRADE_NOTIONAL_USD, Decimal("30"))
        self.assertEqual(MAX_CONCURRENT_POSITIONS_TOTAL, 4)
        self.assertEqual(EVALUATION_CALENDAR_DAYS, 10)

    def test_at_limit_allowed_when_slot_free(self):
        self.assertTrue(check_new_entry(notional_usd="30", open_positions_total=2,
                                        reserved_entry_slots_total=1,
                                        market=Market.CRYPTO_SPOT,
                                        direction=Direction.LONG).approved)

    def test_more_than_30_refused(self):
        result = check_new_entry(notional_usd="30.00001", open_positions_total=0,
                                 reserved_entry_slots_total=0, market=Market.STOCK,
                                 direction=Direction.LONG)
        self.assertEqual(result.reason, "NOTIONAL_OUT_OF_RANGE")

    def test_fifth_position_is_refused(self):
        result = check_new_entry(notional_usd="5", open_positions_total=2,
                                 reserved_entry_slots_total=2, market=Market.STOCK,
                                 direction=Direction.LONG)
        self.assertEqual(result.reason, "MAX_CONCURRENT_POSITIONS")

    def test_crypto_short_refused(self):
        result = check_new_entry(notional_usd="30", open_positions_total=0,
                                 reserved_entry_slots_total=0, market=Market.CRYPTO_SPOT,
                                 direction=Direction.SHORT)
        self.assertEqual(result.reason, "CRYPTO_SPOT_SHORT_UNSUPPORTED")

    def test_stock_short_needs_entitlement_and_whole_share(self):
        base = dict(notional_usd="30", open_positions_total=0,
                    reserved_entry_slots_total=0, market=Market.STOCK,
                    direction=Direction.SHORT)
        self.assertFalse(check_new_entry(**base, stock_short_eligible=True).approved)
        self.assertFalse(check_new_entry(**base, stock_short_whole_share=True).approved)
        self.assertTrue(check_new_entry(**base, stock_short_whole_share=True, stock_short_eligible=True).approved)

    def test_invalid_quantities(self):
        for value in ["nan", "inf", "-1", "0", "invalid"]:
            with self.subTest(value=value):
                self.assertFalse(check_new_entry(notional_usd=value,
                    open_positions_total=0, reserved_entry_slots_total=0,
                    market=Market.STOCK, direction=Direction.LONG).approved)


if __name__ == "__main__":
    unittest.main()
