from conftest import free_month, pnl, add, sfx
def test_rules(c):
    y,m = free_month(); s=f"{y}-{m:02d}-01"; e=f"{y}-{m:02d}-28"; d=f"{y}-{m:02d}-10"; t=sfx()
    b = pnl(c,s,e)["total"]
    add(c,"sales-returns",reference=f"tscheck-ret-{t}",amount=25,date=d)
    b2 = pnl(c,s,e)["total"]; assert round(b["net_revenue"]-b2["net_revenue"],3)==25.0
    mat=f"tscheck Resin {t}"
    add(c,"raw-material-purchases",supplier="tscheck",material=mat,qty=100,unit_cost=2,date=d)
    add(c,"raw-material-purchases",supplier="tscheck",material=mat,qty=100,unit_cost=4,date=d)
    b3 = pnl(c,s,e)["total"]; assert round(b3["cogs"]-b2["cogs"],3)==0.0
    r = add(c,"raw-material-consumption",material=mat.lower(),qty_used=50,production_run="tscheck",date=d)
    assert r["computed"]["value"]==150.0
    r2 = add(c,"raw-material-consumption",material=f"tscheck never {t}",qty_used=5,production_run="tscheck",date=d)
    assert r2["computed"]["value"]==0.0
    lst = c.get("/records/raw-material-consumption", params={"limit":1000}).json()["items"]
    row=[x for x in lst if x["id"]==r2["id"]]
    assert row and "No purchase cost found" in str(row[0])
    b4 = pnl(c,s,e)["total"]; assert round(b4["cogs"]-b3["cogs"],3)==150.0
    add(c,"direct-labour",description=f"tscheck-{t}",hours=8,rate=1.25,date=d)
    add(c,"machine-running-cost",description=f"tscheck-{t}",amount=20,production_run="x",date=d)
    b5 = pnl(c,s,e)["total"]; assert round(b5["cogs"]-b4["cogs"],3)==30.0
    prod=f"tscheck Pipe {t}"
    add(c,"finished-goods",product=prod,qty=200,total_production_cost=500,date=d)
    rep = pnl(c,s,e); assert round(rep["total"]["cogs"]-b5["cogs"],3)==0.0
    cpu=[p for p in rep["cost_per_unit"]["products"] if p["product"]==prod]
    assert cpu and cpu[0]["cost_per_unit"]==2.5
