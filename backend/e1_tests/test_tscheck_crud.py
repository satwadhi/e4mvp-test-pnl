from conftest import free_month, pnl, add, sfx
def test_sale_crud_revenue(c):
    y,m = free_month(); s=f"{y}-{m:02d}-01"; e=f"{y}-{m:02d}-28"
    base = pnl(c,s,e)["total"]["net_revenue"]
    r = add(c,"sales",customer=f"tscheck-crud-{sfx()}",product="P",qty=10,unit_price=12.5,date=f"{y}-{m:02d}-05")
    assert r["computed"]["total"] == 125.0
    assert round(pnl(c,s,e)["total"]["net_revenue"]-base,3) == 125.0
    u = c.put(f"/records/sales/{r['id']}", json={**r["values"],"qty":20}); assert u.status_code==200, u.text
    assert round(pnl(c,s,e)["total"]["net_revenue"]-base,3) == 250.0
    assert c.delete(f"/records/sales/{r['id']}").status_code==200
    assert round(pnl(c,s,e)["total"]["net_revenue"]-base,3) == 0.0
def test_validation(c):
    r = c.post("/records/sales", json={}); assert r.status_code in (400,422)
    assert r.json()["detail"]["errors"]["customer"] == "Required"
    r = c.post("/records/sales", json={"customer":"tscheck-v","product":"p","qty":0,"unit_price":-1,"date":"2050-01-01"})
    assert r.status_code in (400,422); er=r.json()["detail"]["errors"]
    assert er["qty"]=="Must be greater than 0" and er["unit_price"]=="Must be greater than 0"
def test_18_categories_and_utilities(c):
    cats = c.get("/categories").json()["categories"]; assert len(cats)==18
    u = [x for x in cats if x["slug"]=="utilities"][0]
    assert [f for f in u["fields"] if f["key"]=="type"][0]["options"]==["Electricity","Water","Gas"]
