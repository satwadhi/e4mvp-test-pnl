def test_dashboard(c):
    d = c.get("/dashboard").json()
    assert d["month"] == "2026-10"
    for k in ["net_revenue","cogs","opex","gross_profit","net_profit"]: assert k in d["cards"]
    assert len(d["trend"]) == 12 and d["trend"][-1]["period"] == "2026-10"
