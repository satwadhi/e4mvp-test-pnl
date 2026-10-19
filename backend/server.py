from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

import logging  # noqa: E402
import os  # noqa: E402
from datetime import date, datetime, timezone  # noqa: E402
from typing import Any, Dict, Literal  # noqa: E402

from bson import ObjectId  # noqa: E402
from bson.errors import InvalidId  # noqa: E402
from fastapi import APIRouter, Body, Depends, FastAPI, HTTPException, Query  # noqa: E402
from pydantic import BaseModel  # noqa: E402
from starlette.middleware.cors import CORSMiddleware  # noqa: E402

from auth import create_access_token, get_current_user, seed_admin, verify_password  # noqa: E402
from categories import BY_SLUG, CATEGORIES, CONSUMPTION, GROUPS, MONEY, QTY, to_storage, validate_values  # noqa: E402
from core import Record, User, client, db, muscat_today  # noqa: E402
from engine import build_report, compute_line, load_lookup, month_label  # noqa: E402
from money import baisa_to_omr, to_dec  # noqa: E402
from seed import seed_sample_data_once  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(title="Factory P&L Panel API", version="1.0.0",
              openapi_url="/api/openapi.json", docs_url="/api/docs", redoc_url=None)
public = APIRouter(prefix="/api")
private = APIRouter(prefix="/api", dependencies=[Depends(get_current_user)])


class LoginIn(BaseModel):
    email: str
    password: str


def public_user(user: User) -> dict:
    return {"id": user.id, "email": user.email, "name": user.name, "role": user.role}


@public.post("/auth/login", tags=["auth"])
async def login(body: LoginIn):
    doc = await db.users.find_one({"email": body.email.strip().lower()})
    if not doc or not verify_password(body.password, doc["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    user = User.from_mongo(doc)
    return {"access_token": create_access_token(user.id, user.email), "token_type": "bearer", "user": public_user(user)}


@private.get("/auth/me", tags=["auth"])
async def me(user: User = Depends(get_current_user)):
    return public_user(user)


@private.post("/auth/logout", tags=["auth"])
async def logout():
    return {"ok": True}


@private.get("/categories", tags=["records"])
async def list_categories():
    return {"groups": GROUPS, "categories": CATEGORIES}


def get_category(slug: str) -> dict:
    category = BY_SLUG.get(slug)
    if not category:
        raise HTTPException(status_code=404, detail="Unknown category")
    return category


def parse_oid(record_id: str) -> ObjectId:
    try:
        return ObjectId(record_id)
    except (InvalidId, TypeError):
        raise HTTPException(status_code=404, detail="Record not found")


def serialize(category: dict, rec: Record, lookup) -> dict:
    values = {}
    for f in category["fields"]:
        k = f["key"]
        if k == category["period"]:
            values[k] = getattr(rec, k)
        elif f["type"] == MONEY:
            values[k] = baisa_to_omr(rec.values[k])
        elif f["type"] == QTY:
            values[k] = float(to_dec(rec.values[k]))
        else:
            values[k] = rec.values[k]
    computed = {k: (v if k == "warning" or v is None else baisa_to_omr(v))
                for k, v in compute_line(category, rec.values, rec.date, lookup).items()}
    return {"id": rec.id, "category": rec.category, "values": values, "computed": computed,
            "is_sample": rec.is_sample, "created_at": rec.created_at, "updated_at": rec.updated_at}


def clean_or_422(category: dict, payload: dict):
    clean, errors = validate_values(category, payload)
    if errors:
        raise HTTPException(status_code=422, detail={"message": "Please fix the highlighted fields", "errors": errors})
    return to_storage(category, clean)


async def lookup_for(category: dict):
    return await load_lookup() if category["slug"] == CONSUMPTION else None


@private.get("/records/{category}", tags=["records"])
async def list_records(category: str):
    cat = get_category(category)
    docs = await db.records.find({"category": category}).sort([("created_at", -1), ("_id", -1)]).to_list(None)
    lookup = await lookup_for(cat)
    return {"items": [serialize(cat, Record.from_mongo(d), lookup) for d in docs]}


@private.post("/records/{category}", status_code=201, tags=["records"])
async def create_record(category: str, payload: Dict[str, Any] = Body(...)):
    cat = get_category(category)
    period, values = clean_or_422(cat, payload)
    now = datetime.now(timezone.utc)
    rec = Record(category=category, **period, values=values, is_sample=False, created_at=now, updated_at=now)
    result = await db.records.insert_one(rec.to_mongo())
    rec.id = str(result.inserted_id)
    return serialize(cat, rec, await lookup_for(cat))


@private.put("/records/{category}/{record_id}", tags=["records"])
async def update_record(category: str, record_id: str, payload: Dict[str, Any] = Body(...)):
    cat = get_category(category)
    oid = parse_oid(record_id)
    period, values = clean_or_422(cat, payload)
    result = await db.records.update_one(
        {"_id": oid, "category": category},
        {"$set": {**period, "values": values, "updated_at": datetime.now(timezone.utc)}})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Record not found")
    doc = await db.records.find_one({"_id": oid})
    return serialize(cat, Record.from_mongo(doc), await lookup_for(cat))


@private.delete("/records/{category}/{record_id}", tags=["records"])
async def delete_record(category: str, record_id: str):
    get_category(category)
    result = await db.records.delete_one({"_id": parse_oid(record_id), "category": category})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Record not found")
    return {"deleted": True}


@private.get("/reports/pnl", tags=["reports"])
async def pnl_report(start: date = Query(...), end: date = Query(...),
                     granularity: Literal["daily", "monthly"] = Query("monthly")):
    if start > end:
        raise HTTPException(status_code=400, detail="Start date must be before end date")
    return await build_report(start, end, granularity)


@private.get("/dashboard", tags=["reports"])
async def dashboard():
    today = muscat_today()
    start = today.replace(day=1)
    current = await build_report(start, today, "monthly")
    y, m = today.year, today.month - 11
    if m < 1:
        y, m = y - 1, m + 12
    trend = await build_report(date(y, m, 1), today, "monthly")
    key = today.isoformat()[:7]
    return {"month": key, "month_label": month_label(key), "today": today.isoformat(),
            "start": start.isoformat(), "end": today.isoformat(),
            "period_label": f"Month to date: 1–{today.day} {month_label(key)}",
            "cards": current["total"], "has_data": current["has_data"], "trend": trend["rows"]}


@private.get("/settings/sample-data", tags=["settings"])
async def sample_data_status():
    return {"sample_records": await db.records.count_documents({"is_sample": True}),
            "user_records": await db.records.count_documents({"is_sample": {"$ne": True}})}


@private.post("/settings/clear-sample-data", tags=["settings"])
async def clear_sample_data():
    result = await db.records.delete_many({"is_sample": True})
    return {"deleted": result.deleted_count}


app.include_router(public)
app.include_router(private)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=False,
    allow_origins=os.environ["CORS_ORIGINS"].split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    await db.users.create_index("email", unique=True)
    await db.records.create_index([("category", 1), ("created_at", -1)])
    await db.records.create_index("date")
    await db.records.create_index("month")
    await db.records.create_index("is_sample")
    await seed_admin()
    seeded = await seed_sample_data_once()
    if seeded:
        logger.info("Seeded %s sample records", seeded)


@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
