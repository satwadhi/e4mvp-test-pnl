"""Category config + per-category validation (reused by Phase 2 bulk import)."""
import re
from datetime import date

from bson.decimal128 import Decimal128

from money import omr_to_baisa, parse_decimal, round3

TEXT, SELECT, DATE, MONTH, MONEY, QTY = "text", "select", "date", "month", "money", "quantity"

SALES = "sales"
PURCHASES = "raw-material-purchases"
CONSUMPTION = "raw-material-consumption"
LABOUR = "direct-labour"
FINISHED = "finished-goods"

GROUPS = [
    {"key": "revenue", "label": "Revenue"},
    {"key": "cogs", "label": "COGS"},
    {"key": "opex", "label": "Operating Expenses"},
    {"key": "other", "label": "Other"},
]


def F(key, label, type_, **kw):
    return {"key": key, "label": label, "type": type_, **kw}


DATE_F = F("date", "Date", DATE)
MONTH_F = F("month", "Month", MONTH)
AMOUNT = F("amount", "Amount", MONEY)
DESC = F("description", "Description", TEXT)
TOTAL = F("total", "Total", MONEY)


def cat(slug, label, group, fields, amount=None, computed=()):
    period = "month" if any(f["type"] == MONTH for f in fields) else "date"
    return {"slug": slug, "label": label, "group": group, "period": period,
            "fields": fields, "amount": amount, "computed": list(computed)}


CATEGORIES = [
    cat(SALES, "Sales", "revenue",
        [F("customer", "Customer", TEXT), F("product", "Product", TEXT), F("qty", "Quantity", QTY),
         F("unit_price", "Unit price", MONEY), DATE_F], amount="total", computed=[TOTAL]),
    cat("sales-returns", "Sales returns", "revenue", [F("reference", "Reference", TEXT), AMOUNT, DATE_F], amount="amount"),
    cat("other-income", "Other income", "revenue", [DESC, AMOUNT, DATE_F], amount="amount"),
    cat(PURCHASES, "Raw material purchases", "cogs",
        [F("supplier", "Supplier", TEXT), F("material", "Material", TEXT), F("qty", "Quantity", QTY),
         F("unit_cost", "Unit cost", MONEY), DATE_F], computed=[TOTAL]),
    cat(CONSUMPTION, "Raw material consumption", "cogs",
        [F("material", "Material", TEXT), F("qty_used", "Quantity used", QTY),
         F("production_run", "Production run", TEXT), DATE_F],
        amount="value", computed=[F("avg_unit_cost", "Avg unit cost", MONEY), F("value", "Value", MONEY)]),
    cat(LABOUR, "Direct labour", "cogs",
        [DESC, F("hours", "Hours", QTY), F("rate", "Rate per hour", MONEY), DATE_F], amount="total", computed=[TOTAL]),
    cat("machine-running-cost", "Machine running cost", "cogs",
        [DESC, AMOUNT, F("production_run", "Production run", TEXT), DATE_F], amount="amount"),
    cat(FINISHED, "Finished goods produced", "cogs",
        [F("product", "Product", TEXT), F("qty", "Quantity", QTY),
         F("total_production_cost", "Total production cost", MONEY), DATE_F],
        computed=[F("cost_per_unit", "Cost per unit", MONEY)]),
    cat("salaries", "Salaries", "opex", [F("department", "Department", TEXT), AMOUNT, MONTH_F], amount="amount"),
    cat("utilities", "Utilities", "opex",
        [F("type", "Type", SELECT, options=["Electricity", "Water", "Gas"]), AMOUNT, MONTH_F], amount="amount"),
    cat("rent", "Rent", "opex", [AMOUNT, MONTH_F], amount="amount"),
    cat("maintenance-repairs", "Maintenance & repairs", "opex", [DESC, AMOUNT, DATE_F], amount="amount"),
    cat("transportation-logistics", "Transportation & logistics", "opex", [DESC, AMOUNT, DATE_F], amount="amount"),
    cat("marketing-sales", "Marketing & sales", "opex", [DESC, AMOUNT, DATE_F], amount="amount"),
    cat("admin-office", "Admin & office", "opex", [DESC, AMOUNT, DATE_F], amount="amount"),
    cat("depreciation", "Depreciation", "other",
        [F("asset_name", "Asset name", TEXT), F("monthly_charge", "Monthly charge", MONEY), MONTH_F],
        amount="monthly_charge"),
    cat("loan-interest", "Loan interest", "other", [DESC, AMOUNT, MONTH_F], amount="amount"),
    cat("tax-provision", "Tax provision", "other", [DESC, AMOUNT, MONTH_F], amount="amount"),
]

BY_SLUG = {c["slug"]: c for c in CATEGORIES}

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
MONTH_RE = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")


def _clean_field(field, raw):
    s = "" if raw is None else str(raw).strip()
    if s == "":
        return None, "Required"
    t = field["type"]
    if t == TEXT:
        return (s, None) if len(s) <= 200 else (None, "Must be 200 characters or fewer")
    if t == SELECT:
        match = next((o for o in field["options"] if o.lower() == s.lower()), None)
        return (match, None) if match else (None, "Must be one of: " + ", ".join(field["options"]))
    if t == DATE:
        if not DATE_RE.match(s):
            return None, "Invalid date (YYYY-MM-DD)"
        try:
            return date.fromisoformat(s).isoformat(), None
        except ValueError:
            return None, "Invalid date (YYYY-MM-DD)"
    if t == MONTH:
        return (s, None) if MONTH_RE.match(s) else (None, "Invalid month (YYYY-MM)")
    d = parse_decimal(raw)
    if d is None:
        return None, "Must be a number"
    if d <= 0 or round3(d) <= 0:
        return None, "Must be greater than 0"
    return (omr_to_baisa(d) if t == MONEY else round3(d)), None


def validate_values(category: dict, raw: dict):
    """Returns (clean_values, errors). Money -> int baisa, quantity -> Decimal(3dp)."""
    clean, errors = {}, {}
    for field in category["fields"]:
        value, error = _clean_field(field, raw.get(field["key"]))
        if error:
            errors[field["key"]] = error
        else:
            clean[field["key"]] = value
    return clean, errors


def to_storage(category: dict, clean: dict):
    """Returns ({date|month: value}, values) ready for a Record."""
    values = dict(clean)
    period = {category["period"]: values.pop(category["period"])}
    for field in category["fields"]:
        if field["type"] == QTY:
            values[field["key"]] = Decimal128(str(values[field["key"]]))
    return period, values
