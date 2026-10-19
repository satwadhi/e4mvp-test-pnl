"""Backend API tests for Factory P&L Panel."""
import os
import pytest
import requests
from datetime import datetime

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/") or \
           "https://cc2a8ab2-ba2d-42be-bac3-d9a6651bff0e--env-e4-mvp.dp2.internal-preview.eph.sh"
API = f"{BASE_URL}/api"
ADMIN_EMAIL = "admin@factory.om"
ADMIN_PASSWORD = "Admin@12345"


@pytest.fixture(scope="session")
def token():
    r = requests.post(f"{API}/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}, timeout=20)
    assert r.status_code == 200, f"login failed: {r.status_code} {r.text}"
    return r.json()["access_token"]


@pytest.fixture(scope="session")
def auth(token):
    return {"Authorization": f"Bearer {token}"}


# ---------- Auth / public ----------
class TestAuth:
    def test_openapi_public(self):
        r = requests.get(f"{API}/openapi.json", timeout=15)
        assert r.status_code == 200
        assert "openapi" in r.json()

    def test_login_wrong_password(self):
        r = requests.post(f"{API}/auth/login", json={"email": ADMIN_EMAIL, "password": "WRONG"}, timeout=15)
        assert r.status_code == 401
        assert r.json().get("detail") == "Invalid email or password"

    def test_login_ok(self, token):
        assert isinstance(token, str) and len(token) > 20

    def test_me(self, auth):
        r = requests.get(f"{API}/auth/me", headers=auth, timeout=15)
        assert r.status_code == 200
        assert r.json()["email"] == ADMIN_EMAIL

    @pytest.mark.parametrize("path", [
        "/auth/me", "/categories", "/records/sales", "/dashboard",
        "/reports/pnl?start=2026-10-01&end=2026-10-31&granularity=monthly",
        "/settings/sample-data",
    ])
    def test_401_without_token(self, path):
        r = requests.get(f"{API}{path}", timeout=15)
        assert r.status_code == 401, f"{path} should be 401, got {r.status_code}"


# ---------- Categories ----------
class TestCategories:
    def test_list(self, auth):
        r = requests.get(f"{API}/categories", headers=auth, timeout=15)
        assert r.status_code == 200
        data = r.json()
        assert len(data["categories"]) == 18
        slugs = {c["slug"] for c in data["categories"]}
        for s in ["sales", "sales-returns", "other-income", "raw-material-purchases",
                  "raw-material-consumption", "direct-labour", "machine-running-cost",
                  "finished-goods", "salaries", "utilities", "rent", "maintenance-repairs",
                  "transportation-logistics", "marketing-sales", "admin-office",
                  "depreciation", "loan-interest", "tax-provision"]:
            assert s in slugs

    def test_utilities_select_options(self, auth):
        r = requests.get(f"{API}/categories", headers=auth, timeout=15).json()
        util = next(c for c in r["categories"] if c["slug"] == "utilities")
        type_field = next(f for f in util["fields"] if f["key"] == "type")
        assert type_field["options"] == ["Electricity", "Water", "Gas"]


# ---------- Dashboard ----------
class TestDashboard:
    def test_dashboard_cards(self, auth):
        r = requests.get(f"{API}/dashboard", headers=auth, timeout=20)
        assert r.status_code == 200
        d = r.json()
        for k in ["net_revenue", "cogs", "gross_profit", "opex", "operating_profit", "net_profit"]:
            assert k in d["cards"]
        assert len(d["trend"]) == 12


# ---------- Validation ----------
class TestValidation:
    def test_create_requires_fields(self, auth):
        r = requests.post(f"{API}/records/sales", headers=auth, json={}, timeout=15)
        assert r.status_code == 422
        errs = r.json()["detail"]["errors"]
        for k in ["customer", "product", "qty", "unit_price", "date"]:
            assert errs.get(k) == "Required"

    def test_zero_quantity_rejected(self, auth):
        r = requests.post(f"{API}/records/sales", headers=auth, json={
            "customer": "X", "product": "P", "qty": 0, "unit_price": 1, "date": "2025-01-05"}, timeout=15)
        assert r.status_code == 422
        assert "greater than 0" in r.json()["detail"]["errors"]["qty"]


# ---------- Records CRUD + math (JRN-9/11/12/16) ----------
# Use 2025-01 (no seeded data) for isolation.
TEST_MONTH = "2025-01"
TEST_DATE = "2025-01-15"
_created = []  # (slug, id)


def _create(auth, slug, body):
    r = requests.post(f"{API}/records/{slug}", headers=auth, json=body, timeout=15)
    assert r.status_code == 201, f"{slug}: {r.status_code} {r.text}"
    rid = r.json()["id"]
    _created.append((slug, rid))
    return r.json()


class TestRecordsFlow:
    def test_sales_total_computed(self, auth):
        rec = _create(auth, "sales", {"customer": "ACME", "product": "Widget",
                                       "qty": 10, "unit_price": 12.5, "date": TEST_DATE})
        assert rec["computed"]["total"] == 125.0

    def test_sales_return(self, auth):
        _create(auth, "sales-returns", {"reference": "R1", "amount": 25, "date": TEST_DATE})

    def test_purchase_and_consumption_avg_cost(self, auth):
        _create(auth, "raw-material-purchases", {"supplier": "S1", "material": "Resin X",
                                                  "qty": 10, "unit_cost": 100, "date": "2025-01-05"})
        _create(auth, "raw-material-purchases", {"supplier": "S2", "material": "resin x  ",
                                                  "qty": 10, "unit_cost": 200, "date": "2025-01-10"})
        rec = _create(auth, "raw-material-consumption", {"material": "RESIN X", "qty_used": 5,
                                                          "production_run": "P1", "date": "2025-01-20"})
        # weighted avg (10*100 + 10*200)/20 = 150
        assert rec["computed"]["avg_unit_cost"] == 150.0
        assert rec["computed"]["value"] == 750.0
        assert rec["computed"]["warning"] is None

    def test_consumption_no_purchase_warning(self, auth):
        rec = _create(auth, "raw-material-consumption", {"material": "Unknown Alloy",
                      "qty_used": 7, "production_run": "P2", "date": TEST_DATE})
        assert rec["computed"]["value"] == 0
        assert "No purchase cost" in rec["computed"]["warning"]

    def test_labour_total(self, auth):
        rec = _create(auth, "direct-labour", {"description": "line1", "hours": 10,
                                               "rate": 3, "date": TEST_DATE})
        assert rec["computed"]["total"] == 30.0

    def test_finished_goods_cpu_no_cogs(self, auth):
        rec = _create(auth, "finished-goods", {"product": "W1", "qty": 100,
                                                "total_production_cost": 250, "date": TEST_DATE})
        assert rec["computed"]["cost_per_unit"] == 2.5

    def test_rent_monthly(self, auth):
        _create(auth, "rent", {"amount": 310, "month": TEST_MONTH})

    def test_report_math_isolated_month(self, auth):
        r = requests.get(f"{API}/reports/pnl",
                         params={"start": "2025-01-01", "end": "2025-01-31", "granularity": "monthly"},
                         headers=auth, timeout=20)
        assert r.status_code == 200
        data = r.json()
        total = data["total"]
        # Revenue: sales 125 - returns 25 = 100
        assert total["net_revenue"] == 100.0
        # cogs = labour 30 + consumption (750 valid + 0 unknown) = 780, purchases not COGS, FG not COGS
        assert total["cogs"] == 780.0
        assert total["gross_profit"] == -680.0
        # opex = rent 310
        assert total["opex"] == 310.0
        assert total["operating_profit"] == -990.0
        # cost per unit: product W1 qty 100, cost 250 -> 2.5
        cpu_products = {p["product"]: p for p in data["cost_per_unit"]["products"]}
        assert cpu_products["W1"]["cost_per_unit"] == 2.5
        # warnings include unknown alloy
        assert any(w["material"] == "Unknown Alloy" for w in data["warnings"])

    def test_daily_rent_spreading(self, auth):
        r = requests.get(f"{API}/reports/pnl",
                         params={"start": "2025-01-01", "end": "2025-01-10", "granularity": "daily"},
                         headers=auth, timeout=20).json()
        # rent 310 over 31 days, 10 days = 100
        assert abs(r["total"]["opex"] - 100.0) < 0.001

    def test_total_row_sum(self, auth):
        r = requests.get(f"{API}/reports/pnl",
                         params={"start": "2025-01-01", "end": "2025-03-31", "granularity": "monthly"},
                         headers=auth, timeout=20).json()
        assert len(r["rows"]) == 3
        for k in ["net_revenue", "cogs", "opex", "net_profit"]:
            assert abs(sum(row[k] for row in r["rows"]) - r["total"][k]) < 0.01

    def test_empty_range(self, auth):
        r = requests.get(f"{API}/reports/pnl",
                         params={"start": "2024-01-01", "end": "2024-01-31", "granularity": "monthly"},
                         headers=auth, timeout=20).json()
        assert r["has_data"] is False
        assert r["total"]["net_revenue"] == 0

    def test_start_after_end(self, auth):
        r = requests.get(f"{API}/reports/pnl",
                         params={"start": "2025-02-01", "end": "2025-01-01", "granularity": "monthly"},
                         headers=auth, timeout=20)
        assert r.status_code == 400
        assert "before end" in r.json()["detail"].lower()

    def test_update_record(self, auth):
        slug, rid = next((s, i) for s, i in _created if s == "sales")
        r = requests.put(f"{API}/records/{slug}/{rid}", headers=auth, json={
            "customer": "ACME", "product": "Widget", "qty": 20,
            "unit_price": 12.5, "date": TEST_DATE}, timeout=15)
        assert r.status_code == 200
        assert r.json()["computed"]["total"] == 250.0

    def test_list_sorted_newest_first(self, auth):
        r = requests.get(f"{API}/records/sales", headers=auth, timeout=15).json()
        if len(r["items"]) >= 2:
            a, b = r["items"][0]["created_at"], r["items"][1]["created_at"]
            assert a >= b


# ---------- Reconcile seeded P&L (JRN-22 / Q-1) ----------
class TestSeededReconcile:
    def test_pnl_vs_hand_computation(self, auth):
        # Pick a seeded month (May 2026)
        start, end = "2026-05-01", "2026-05-31"
        r = requests.get(f"{API}/reports/pnl",
                         params={"start": start, "end": end, "granularity": "monthly"},
                         headers=auth, timeout=30).json()
        if not r["has_data"]:
            pytest.skip("No seed data in May 2026")
        total = r["total"]
        # Sanity: gross = net_revenue - cogs; operating = gross - opex; net = operating - other
        assert abs(total["gross_profit"] - (total["net_revenue"] - total["cogs"])) < 0.01
        assert abs(total["operating_profit"] - (total["gross_profit"] - total["opex"])) < 0.01
        assert abs(total["net_profit"] - (total["operating_profit"] - total["other"])) < 0.01


# ---------- Settings ----------
class TestSettings:
    def test_sample_data_status(self, auth):
        r = requests.get(f"{API}/settings/sample-data", headers=auth, timeout=15)
        assert r.status_code == 200
        d = r.json()
        assert "sample_records" in d and "user_records" in d
        assert d["sample_records"] > 0  # seeded


# ---------- Teardown: cleanup user records we created ----------
@pytest.fixture(scope="session", autouse=True)
def _cleanup(auth):
    yield
    for slug, rid in _created:
        try:
            requests.delete(f"{API}/records/{slug}/{rid}", headers=auth, timeout=10)
        except Exception:
            pass
