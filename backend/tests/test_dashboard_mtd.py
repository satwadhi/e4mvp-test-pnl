"""Dashboard month-to-date checks (JRN-23, JRN-24). Run: python /app/backend/tests/test_dashboard_mtd.py"""
import os
from calendar import monthrange
from datetime import date

import requests
from dotenv import dotenv_values

API = dotenv_values("/app/frontend/.env")["REACT_APP_BACKEND_URL"] + "/api"
ENV = dotenv_values("/app/backend/.env")
KEYS = ["net_revenue", "cogs", "gross_profit", "opex", "operating_profit", "other", "net_profit", "total_cost"]
MONTHLY = ["salaries", "utilities", "rent", "depreciation", "loan-interest", "tax-provision"]
AMOUNT_KEY = {"depreciation": "monthly_charge"}


def main():
    tok = requests.post(f"{API}/auth/login", json={"email": ENV["ADMIN_EMAIL"], "password": ENV["ADMIN_PASSWORD"]}).json()["access_token"]
    s = requests.Session()
    s.headers["Authorization"] = f"Bearer {tok}"

    dash = s.get(f"{API}/dashboard").json()
    today = date.fromisoformat(dash["today"])
    start = today.replace(day=1)
    last = today.replace(day=monthrange(today.year, today.month)[1])
    mon = date(2000, today.month, 1).strftime("%b")
    assert dash["period_label"] == f"Month to date: 1–{today.day} {mon} {today.year}", dash["period_label"]

    daily = s.get(f"{API}/reports/pnl", params={"start": start, "end": today, "granularity": "daily"}).json()
    for k in KEYS:
        assert dash["cards"][k] == daily["total"][k], (k, dash["cards"][k], daily["total"][k])
    trend_cur = dash["trend"][-1]
    assert trend_cur["period"] == today.isoformat()[:7]
    for k in KEYS:
        assert trend_cur[k] == dash["cards"][k], (k, trend_cur[k])

    # past months in the trend stay full-month
    prev_key = dash["trend"][-2]["period"]
    y, m = map(int, prev_key.split("-"))
    full = s.get(f"{API}/reports/pnl", params={"start": date(y, m, 1), "end": date(y, m, monthrange(y, m)[1]), "granularity": "monthly"}).json()
    for k in KEYS:
        assert dash["trend"][-2][k] == full["total"][k], (k, prev_key)

    # monthly items: elapsed-day share via cumulative per-day spreading
    days = monthrange(today.year, today.month)[1]
    share = lambda a: (2 * a * today.day + days) // (2 * days)  # noqa: E731
    mk = today.isoformat()[:7]
    opex_monthly = other_monthly = 0
    for slug in MONTHLY:
        for r in s.get(f"{API}/records/{slug}").json()["items"]:
            if r["values"]["month"] == mk:
                b = share(round(r["values"][AMOUNT_KEY.get(slug, "amount")] * 1000))
                if slug in ("depreciation", "loan-interest", "tax-provision"):
                    other_monthly += b
                else:
                    opex_monthly += b
    assert round(dash["cards"]["other"] * 1000) == other_monthly, (dash["cards"]["other"], other_monthly)
    print("monthly opex share (baisa):", opex_monthly, "other:", other_monthly)

    # JRN-24: a sale after today does not change the dashboard but shows in full-month report
    created = None
    if today < last:
        before_dash = dash["cards"]["net_revenue"]
        full_before = s.get(f"{API}/reports/pnl", params={"start": start, "end": last}).json()["total"]["net_revenue"]
        created = s.post(f"{API}/records/sales", json={"customer": "mtdcheck", "product": "X", "qty": 2, "unit_price": 5,
                                                          "date": last.isoformat()}).json()["id"]
        try:
            assert s.get(f"{API}/dashboard").json()["cards"]["net_revenue"] == before_dash
            full_after = s.get(f"{API}/reports/pnl", params={"start": start, "end": last}).json()["total"]["net_revenue"]
            assert round((full_after - full_before) * 1000) == 10000, (full_before, full_after)
        finally:
            s.delete(f"{API}/records/sales/{created}")
    print("PASS", dash["period_label"], dash["cards"])


if __name__ == "__main__":
    main()
