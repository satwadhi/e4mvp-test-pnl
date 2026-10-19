import httpx
from conftest import BASE
def test_login_ok_and_bad():
    assert httpx.post(f"{BASE}/auth/login", json={"email":"admin@factory.om","password":"Admin@12345"}).status_code == 200
    r = httpx.post(f"{BASE}/auth/login", json={"email":"admin@factory.om","password":"wrong"})
    assert r.status_code == 401 and "Invalid email or password" in r.text
def test_no_signup():
    for p in ["/auth/signup","/auth/register","/signup","/register"]:
        assert httpx.post(f"{BASE}{p}", json={}).status_code in (404,405)
def test_data_routes_401():
    for p in ["/records/sales","/dashboard","/reports/pnl?start=2026-05-01&end=2026-05-31&granularity=monthly","/settings/sample-data","/categories"]:
        assert httpx.get(f"{BASE}{p}").status_code == 401, p
    assert httpx.post(f"{BASE}/settings/clear-sample-data").status_code == 401
