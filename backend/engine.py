from bisect import bisect_right
from calendar import monthrange
from collections import defaultdict
from datetime import date, timedelta
from decimal import Decimal

from categories import BY_SLUG, CATEGORIES, CONSUMPTION, FINISHED, LABOUR, PURCHASES, SALES
from core import Record, db
from money import baisa_to_omr, round_int, to_dec

NO_COST = "No purchase cost found"
MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def norm(s: str) -> str:
    return s.strip().lower()


class CostLookup:
    """Weighted average purchase cost per material, as of a date (inclusive)."""

    def __init__(self, purchases):
        grouped = defaultdict(list)
        for p in sorted(purchases, key=lambda r: r.date):
            qty = to_dec(p.values["qty"])
            grouped[norm(p.values["material"])].append((p.date, qty, qty * p.values["unit_cost"]))
        self.data = {}
        for material, rows in grouped.items():
            dates, cq, cc, q, c = [], [], [], Decimal(0), Decimal(0)
            for d, qty, cost in rows:
                q, c = q + qty, c + cost
                dates.append(d)
                cq.append(q)
                cc.append(c)
            self.data[material] = (dates, cq, cc)

    def totals(self, material: str, on_date: str):
        entry = self.data.get(norm(material))
        if not entry:
            return None
        idx = bisect_right(entry[0], on_date)
        return None if idx == 0 else (entry[1][idx - 1], entry[2][idx - 1])


async def load_lookup(up_to: str = None):
    query = {"category": PURCHASES}
    if up_to:
        query["date"] = {"$lte": up_to}
    return CostLookup([Record.from_mongo(d) async for d in db.records.find(query)])


def compute_line(category: dict, values: dict, rec_date, lookup) -> dict:
    """Computed amounts in baisa (int) for one record."""
    slug = category["slug"]
    if slug == SALES:
        return {"total": round_int(to_dec(values["qty"]) * values["unit_price"])}
    if slug == PURCHASES:
        return {"total": round_int(to_dec(values["qty"]) * values["unit_cost"])}
    if slug == LABOUR:
        return {"total": round_int(to_dec(values["hours"]) * values["rate"])}
    if slug == FINISHED:
        return {"cost_per_unit": round_int(Decimal(values["total_production_cost"]) / to_dec(values["qty"]))}
    if slug == CONSUMPTION:
        found = lookup.totals(values["material"], rec_date)
        if not found:
            return {"avg_unit_cost": None, "value": 0, "warning": NO_COST}
        q, c = found
        return {"avg_unit_cost": round_int(c / q), "value": round_int(to_dec(values["qty_used"]) * c / q), "warning": None}
    return {}


def pl_amount(category: dict, values: dict, computed: dict) -> int:
    key = category["amount"]
    return computed[key] if key in computed else values[key]


def spread_month(amount: int, month_key: str):
    """Evenly spread baisa over the days of a month; cumulative rounding so the days sum exactly."""
    y, m = map(int, month_key.split("-"))
    days = monthrange(y, m)[1]
    cum = lambda i: (2 * amount * i + days) // (2 * days)  # noqa: E731
    return [(date(y, m, i), cum(i) - cum(i - 1)) for i in range(1, days + 1)]


def month_keys(start: date, end: date):
    keys, y, m = [], start.year, start.month
    while (y, m) <= (end.year, end.month):
        keys.append(f"{y}-{m:02d}")
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    return keys


def month_label(key: str) -> str:
    y, m = key.split("-")
    return f"{MONTH_NAMES[int(m) - 1]} {y}"


def day_label(iso: str) -> str:
    y, m, d = iso.split("-")
    return f"{d} {MONTH_NAMES[int(m) - 1]} {y}"


def summarize(cats: dict) -> dict:
    g = lambda *slugs: sum(cats.get(s, 0) for s in slugs)  # noqa: E731
    by_group = defaultdict(int)
    for c in CATEGORIES:
        if c["amount"] and c["group"] != "revenue":
            by_group[c["group"]] += cats.get(c["slug"], 0)
    net_revenue = g(SALES, "other-income") - g("sales-returns")
    cogs, opex, other = by_group["cogs"], by_group["opex"], by_group["other"]
    gross = net_revenue - cogs
    operating = gross - opex
    return {"net_revenue": net_revenue, "cogs": cogs, "gross_profit": gross, "opex": opex,
            "operating_profit": operating, "other": other, "net_profit": operating - other,
            "total_cost": cogs + opex + other}


def to_omr(d: dict) -> dict:
    return {k: baisa_to_omr(v) for k, v in d.items()}


async def build_report(start: date, end: date, granularity: str) -> dict:
    s, e = start.isoformat(), end.isoformat()
    cursor = db.records.find({"$or": [{"date": {"$gte": s, "$lte": e}}, {"month": {"$in": month_keys(start, end)}}]})
    docs = [Record.from_mongo(d) async for d in cursor]
    lookup = await load_lookup(e)

    buckets = defaultdict(lambda: defaultdict(int))
    products, warnings = {}, []
    for r in docs:
        category = BY_SLUG.get(r.category)
        if not category:
            continue
        computed = compute_line(category, r.values, r.date, lookup)
        if r.category == FINISHED:
            p = products.setdefault(norm(r.values["product"]), {"product": r.values["product"].strip(), "qty": Decimal(0), "cost": 0})
            p["qty"] += to_dec(r.values["qty"])
            p["cost"] += r.values["total_production_cost"]
        if r.category == CONSUMPTION and computed.get("warning"):
            warnings.append({"id": r.id, "date": r.date, "material": r.values["material"],
                             "qty_used": float(to_dec(r.values["qty_used"])), "message": NO_COST})
        if not category["amount"]:
            continue
        amount = pl_amount(category, r.values, computed)
        if r.month:
            for d, share in spread_month(amount, r.month):
                if start <= d <= end:
                    buckets[d.isoformat()][r.category] += share
        else:
            buckets[r.date][r.category] += amount

    daily = granularity == "daily"
    periods = {}
    d = start
    while d <= end:
        key = d.isoformat() if daily else d.isoformat()[:7]
        periods.setdefault(key, defaultdict(int))
        d += timedelta(days=1)
    totals = defaultdict(int)
    for day, cats in buckets.items():
        key = day if daily else day[:7]
        for slug, amt in cats.items():
            periods[key][slug] += amt
            totals[slug] += amt

    rows = [{"period": k, "label": day_label(k) if daily else month_label(k), **to_omr(summarize(c))}
            for k, c in periods.items()]
    expense_breakdown = [
        {"slug": c["slug"], "label": c["label"], "group": c["group"], "amount": baisa_to_omr(totals.get(c["slug"], 0))}
        for c in CATEGORIES if c["amount"] and c["group"] != "revenue"
    ]
    revenue_breakdown = [
        {"slug": c["slug"], "label": c["label"], "amount": baisa_to_omr(totals.get(c["slug"], 0))}
        for c in CATEGORIES if c["group"] == "revenue"
    ]

    def cpu(qty, cost):
        return {"qty": float(qty), "total_cost": baisa_to_omr(cost),
                "cost_per_unit": baisa_to_omr(round_int(Decimal(cost) / qty)) if qty else None}

    product_rows = [{"product": p["product"], **cpu(p["qty"], p["cost"])}
                    for p in sorted(products.values(), key=lambda p: p["product"].lower())]
    overall = cpu(sum((p["qty"] for p in products.values()), Decimal(0)), sum(p["cost"] for p in products.values()))

    return {
        "start": s, "end": e, "granularity": granularity, "has_data": bool(docs),
        "rows": rows, "total": to_omr(summarize(totals)),
        "expense_breakdown": expense_breakdown, "revenue_breakdown": revenue_breakdown,
        "cost_per_unit": {"products": product_rows, "overall": overall},
        "warnings": warnings,
    }
