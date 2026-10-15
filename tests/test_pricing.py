from datetime import date

from app.services import pricing


def _coupon(**kw):
    base = {"kind": "percent", "value": 10, "max_uses": 5, "used_count": 0, "expires_on": "2026-10-31"}
    base.update(kw)
    return base


def test_percent_discount():
    assert pricing.calc_discount(1000, _coupon(kind="percent", value=10)) == 100


def test_percent_discount_rounds_down():
    assert pricing.calc_discount(999, _coupon(kind="percent", value=10)) == 99


def test_fixed_discount():
    assert pricing.calc_discount(1000, _coupon(kind="fixed", value=300)) == 300


def test_coupon_usable():
    assert pricing.is_coupon_usable(_coupon(), date(2026, 10, 1))


def test_coupon_expired():
    assert not pricing.is_coupon_usable(_coupon(), date(2026, 11, 1))


def test_coupon_usage_limit():
    result = pricing.is_coupon_usable(_coupon(used_count=5), date(2026, 10, 1))
    assert result is not None


def test_calc_total_with_shipping():
    assert pricing.calc_total(800, 0, [{"type": "shipping", "amount": 500}]) == 1380
