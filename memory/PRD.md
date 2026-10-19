# Factory P&L Panel — PRD

## Original problem statement
Phase 1 of a Factory Profit & Loss panel (FastAPI + React + MongoDB). Spec: /app/memory/product/overview.md, phase1/requirement.md (REQ-1..30, Q-1..6), phase1/journeys.md (JRN-1..22). Single admin JWT auth (env-seeded, no signup), OMR 3dp, 18 categories manual CRUD, P&L engine, dashboard, reports, sample data + clear. Phase 2 (Excel templates/import, Excel/PDF export) out of scope.

## Persona
- Admin (only user): factory owner/accountant.

## Architecture
- backend/: core.py (Mongo, Record/User BaseDocument models, Muscat TZ), money.py (int baisa, Decimal), categories.py (18-category config + `validate_values` / `to_storage`, reusable for Phase 2 import), engine.py (CostLookup weighted avg, spread_month cumulative rounding, build_report), auth.py (bcrypt + PyJWT Bearer), seed.py (once, meta flag), server.py (routes).
- Storage: single `records` collection {category, date|month, values (money=int baisa, qty=Decimal128), is_sample, created_at}.
- frontend/: config-driven CategoryPage/RecordFormDialog from GET /api/categories; Dashboard, Reports (recharts), Settings. Sidebar becomes drawer < 1280px.

## Implemented (2026-10-19)
- F-1..F-9 complete; testing iteration 1: backend 31/31, frontend all journeys pass.
- Endpoints: /api/auth/login|me|logout, /api/categories, /api/records/{slug}[/{id}], /api/reports/pnl, /api/dashboard, /api/settings/sample-data, /api/settings/clear-sample-data, /api/openapi.json, /api/docs.
- Seed: 376 sample records May–Oct 2026 (Al-Batinah-style PVC pipe factory), July is a slow (loss) month.

## Backlog
- P0 (Phase 2): F-10 Excel templates per category, F-11 upload with preview/confirm + per-row errors (reuse categories.validate_values), F-12 Excel export, F-13 PDF export.
- P1: list filtering/search + pagination on category pages; brute-force login lockout.
- P2: audit log of edits/deletes.

## Update (2026-10-19, after Phase 1)
- REQ-31..33 / JRN-23..24: Dashboard is month-to-date (1st → today, Asia/Muscat), monthly items use the same per-day spreading, future-dated records excluded, label "Month to date: 1–D Mon YYYY", trend current month = MTD. Test: backend/tests/test_dashboard_mtd.py (passes).
- Fixed signed red/green colours (Money component), key-spread console warning. DB reset to 376 sample / 0 other.

