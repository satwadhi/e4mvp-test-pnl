from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from bson.decimal128 import Decimal128

THOUSANDTH = Decimal("0.001")


def parse_decimal(value):
    if isinstance(value, bool):
        return None
    try:
        d = Decimal(str(value).strip().replace(",", ""))
    except (InvalidOperation, ValueError):
        return None
    return d if d.is_finite() else None


def round3(d: Decimal) -> Decimal:
    return d.quantize(THOUSANDTH, rounding=ROUND_HALF_UP)


def round_int(d) -> int:
    return int(Decimal(d).quantize(Decimal(1), rounding=ROUND_HALF_UP))


def omr_to_baisa(d: Decimal) -> int:
    return round_int(d * 1000)


def baisa_to_omr(b: int) -> float:
    return float(Decimal(b) / 1000)


def to_dec(v) -> Decimal:
    return v.to_decimal() if isinstance(v, Decimal128) else Decimal(str(v))
