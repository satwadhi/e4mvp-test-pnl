import random, uuid, httpx, pytest
BASE = "http://localhost:8001/api"

@pytest.fixture(scope="session")
def c():
    r = httpx.post(f"{BASE}/auth/login", json={"email": "admin@factory.om", "password": "Admin@12345"})
    assert r.status_code == 200
    cl = httpx.Client(base_url=BASE, headers={"Authorization": f"Bearer {r.json()['access_token']}"}, timeout=30)
    yield cl

def sfx(): return uuid.uuid4().hex[:6]

def free_month():
    # random month far in the future -> no seed data there
    y = random.randint(2040, 2090); m = random.choice([1, 3, 5, 7, 8, 10, 12])  # 31-day months
    return y, m

def pnl(c, start, end, g="monthly"):
    r = c.get("/reports/pnl", params={"start": start, "end": end, "granularity": g}); assert r.status_code == 200, r.text
    return r.json()

def add(c, cat, **v):
    r = c.post(f"/records/{cat}", json=v); assert r.status_code in (200, 201), r.text; return r.json()
