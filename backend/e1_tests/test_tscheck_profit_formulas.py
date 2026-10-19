from conftest import pnl
CATS=None
def amt(rec, cat):
    a = cat["amount"]
    return rec["computed"][a] if a in rec.get("computed",{}) else rec["values"][a]
def test_hand_calc(c):
    cats = c.get("/categories").json()["categories"]
    for mon,last in [("2026-06","30"),("2026-07","31")]:
        g={"revenue":0,"cogs":0,"opex":0,"other":0}
        for cat in cats:
            if not cat["amount"]: continue
            items = c.get(f"/records/{cat['slug']}", params={"limit":5000}).json()["items"]
            for r in items:
                key = r["values"].get("date","") if cat["period"]=="date" else r["values"].get("month","")
                if not key.startswith(mon): continue
                v = amt(r,cat)
                if cat["slug"]=="sales-returns": v=-v
                g[cat["group"]]+=v
        row = pnl(c,f"{mon}-01",f"{mon}-{last}")["rows"][0]
        gross=g["revenue"]-g["cogs"]; op=gross-g["opex"]; net=op-g["other"]
        assert abs(round(g["revenue"],3)-row["net_revenue"])<0.0005
        assert abs(round(gross,3)-row["gross_profit"])<0.0005
        assert abs(round(op,3)-row["operating_profit"])<0.0005
        assert abs(round(net,3)-row["net_profit"])<0.0005
        assert abs(round(row["operating_profit"]-row["other"],3)-row["net_profit"])<0.0005
