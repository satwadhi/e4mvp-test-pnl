# DESTRUCTIVE: runs last (zz). Removes all is_sample records.
from conftest import add, sfx
def test_clear_sample(c):
    name=f"tscheck-own-{sfx()}"
    own = add(c,"sales",customer=name,product="P",qty=2,unit_price=5,date="2026-10-15")
    r = c.post("/settings/clear-sample-data"); assert r.status_code==200, r.text
    s = c.get("/settings/sample-data").json(); assert s["sample_records"]==0 and s["user_records"]>=1
    items = c.get("/records/sales", params={"limit":5000}).json()["items"]
    assert any(i["id"]==own["id"] for i in items) and not any(i["is_sample"] for i in items)
    for cat in c.get("/categories").json()["categories"]:
        assert not any(i["is_sample"] for i in c.get(f"/records/{cat['slug']}", params={"limit":5000}).json()["items"])
    d = c.get("/dashboard").json()["cards"]; assert d["net_revenue"]>=10.0
