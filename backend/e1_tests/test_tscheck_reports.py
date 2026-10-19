from conftest import free_month, pnl, add, sfx
def test_monthly_totals(c):
    r = pnl(c,"2026-05-01","2026-07-31"); assert len(r["rows"])==3
    for k in ["net_revenue","cogs","gross_profit","opex","operating_profit","other","net_profit"]:
        assert abs(round(sum(x[k] for x in r["rows"]),3)-r["total"][k])<0.0015, k
def test_daily_rent(c):
    y,m=free_month(); mon=f"{y}-{m:02d}"
    b = pnl(c,f"{mon}-01",f"{mon}-10","daily")["total"]["opex"]
    add(c,"rent",amount=310,month=mon)
    r = pnl(c,f"{mon}-01",f"{mon}-10","daily")
    assert len(r["rows"])==10 and round(r["total"]["opex"]-b,3)==100.0
    assert r["rows"][0]["opex"]>=10.0
def test_empty_and_invalid(c):
    r = pnl(c,"2099-02-01","2099-02-28"); assert r["has_data"] is False and r["total"]["net_profit"]==0
    r = c.get("/reports/pnl", params={"start":"2026-06-10","end":"2026-06-01","granularity":"monthly"})
    assert r.status_code==400 and "Start date must be before end date" in r.text
