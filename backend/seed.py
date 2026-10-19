import random
from calendar import monthrange
from datetime import datetime, time, timedelta

from categories import BY_SLUG, to_storage, validate_values
from core import MUSCAT, Record, db, muscat_today

MATERIALS = [("PVC Resin", "Oman Polymers LLC", 0.480), ("Calcium Carbonate", "Al Hajar Minerals", 0.090),
             ("Heat Stabilizer", "Gulf Chem Trading", 1.850)]
PRODUCTS = [("PVC Pipe 110mm", (5.8, 6.6), (250, 600), 3.40), ("PVC Pipe 50mm", (2.2, 2.6), (300, 700), 1.30),
            ("PVC Elbow 110mm", (0.9, 1.2), (600, 1200), 0.55)]
CUSTOMERS = ["Al Noor Trading", "Muscat Building Supplies", "Sohar Contracting LLC", "Nizwa Hardware",
             "Salalah Projects Co", "Barka Plumbing Centre", "Al Rusayl Industrial Supplies"]


def _months(today, n=6):
    y, m, out = today.year, today.month, []
    for _ in range(n):
        out.append((y, m))
        y, m = (y - 1, 12) if m == 1 else (y, m - 1)
    return list(reversed(out))


def build_sample_rows(today):
    rng = random.Random(2026)
    rows = []
    money = lambda a, b: f"{rng.uniform(a, b):.3f}"  # noqa: E731

    for idx, (y, m) in enumerate(_months(today)):
        last = monthrange(y, m)[1]
        max_day = today.day if (y, m) == (today.year, today.month) else last
        mk, tag = f"{y}-{m:02d}", f"{y % 100:02d}{m:02d}"
        slow = 0.45 if idx == 2 else 1.0

        def add(slug, day=None, **values):
            if day is not None:
                if day > max_day:
                    return
                values["date"] = f"{y}-{m:02d}-{day:02d}"
            else:
                values["month"] = mk
            rows.append((slug, values))

        for day, (mat, sup, cost), qty in [(1, MATERIALS[0], 7500), (2, MATERIALS[1], 4000),
                                           (2, MATERIALS[2], 300), (15, MATERIALS[0], 7500)]:
            add("raw-material-purchases", day, supplier=sup, material=mat, qty=qty,
                unit_cost=f"{cost * rng.uniform(0.95, 1.06):.3f}")
        for run, day in enumerate([4, 10, 17, 24], start=1):
            run_id = f"RUN-{tag}-{run}"
            add("raw-material-consumption", day, material="PVC Resin", qty_used=rng.randint(3000, 3600), production_run=run_id)
            add("raw-material-consumption", day, material="Calcium Carbonate", qty_used=rng.randint(600, 900), production_run=run_id)
            add("raw-material-consumption", day, material="Heat Stabilizer", qty_used=rng.randint(40, 60), production_run=run_id)
        for day in [10, 20, 28]:
            add("machine-running-cost", day, description="Extruder power & consumables", amount=money(180, 320),
                production_run=f"RUN-{tag}-{min(4, day // 7)}")
        for week, day in enumerate([7, 14, 21, 28], start=1):
            add("direct-labour", day, description=f"Production crew wages - week {week}",
                hours=rng.randint(180, 230), rate=money(1.6, 1.9))
        for day in [14, 28]:
            for name, _, (lo, hi), base in PRODUCTS:
                qty = rng.randint(int(lo * 3), int(hi * 3))
                add("finished-goods", day, product=name, qty=qty, total_production_cost=f"{qty * base * rng.uniform(0.95, 1.05):.3f}")

        for day in sorted(rng.randint(1, last) for _ in range(16)):
            name, (plo, phi), (qlo, qhi), _ = rng.choice(PRODUCTS)
            add("sales", day, customer=rng.choice(CUSTOMERS), product=name,
                qty=max(1, int(rng.randint(qlo, qhi) * slow)), unit_price=money(plo, phi))
        for n in range(rng.randint(1, 2)):
            add("sales-returns", rng.randint(5, 27), reference=f"CN-{tag}-{n + 1:02d}", amount=money(40, 220))
        add("other-income", rng.randint(18, 27), description="Scrap PVC sale", amount=money(120, 260))

        for dept, amt in [("Production", 2650), ("Administration", 1450), ("Sales", 1100)]:
            add("salaries", department=dept, amount=f"{amt:.3f}")
        add("utilities", type="Electricity", amount=money(520, 760))
        add("utilities", type="Water", amount=money(85, 130))
        add("utilities", type="Gas", amount=money(140, 210))
        add("rent", amount="1200.000")
        add("maintenance-repairs", rng.randint(3, 26), description="Extruder screw servicing", amount=money(90, 380))
        add("transportation-logistics", rng.randint(3, 13), description="Delivery to Sohar site", amount=money(110, 260))
        add("transportation-logistics", rng.randint(14, 27), description="Truck hire - Nizwa deliveries", amount=money(110, 260))
        add("marketing-sales", rng.randint(5, 25), description=rng.choice(["Trade fair booth", "Social media ads", "Product brochures"]),
            amount=money(150, 400))
        add("admin-office", rng.randint(2, 12), description="Office supplies", amount=money(40, 110))
        add("admin-office", rng.randint(13, 26), description="Internet & telephone", amount=money(60, 160))
        add("depreciation", asset_name="Extrusion Line 1", monthly_charge="425.000")
        add("depreciation", asset_name="Forklift", monthly_charge="95.000")
        add("depreciation", asset_name="Factory fit-out", monthly_charge="150.000")
        add("loan-interest", description="Bank Muscat term loan interest", amount="312.500")
        add("tax-provision", description="Corporate income tax provision", amount=money(180, 260))
    return rows


async def seed_sample_data_once():
    if await db.meta.find_one({"_id": "sample_seeded"}):
        return 0
    docs = []
    for i, (slug, raw) in enumerate(build_sample_rows(muscat_today())):
        category = BY_SLUG[slug]
        clean, errors = validate_values(category, raw)
        if errors:
            raise ValueError(f"Invalid sample row {slug}: {errors}")
        period, values = to_storage(category, clean)
        day = period.get("date") or f"{period['month']}-01"
        created = datetime.combine(datetime.fromisoformat(day).date(), time(8, 0), MUSCAT) + timedelta(seconds=i)
        docs.append(Record(category=slug, **period, values=values, is_sample=True,
                           created_at=created, updated_at=created).to_mongo())
    if docs:
        await db.records.insert_many(docs)
    await db.meta.insert_one({"_id": "sample_seeded", "count": len(docs), "at": datetime.now(MUSCAT)})
    return len(docs)
