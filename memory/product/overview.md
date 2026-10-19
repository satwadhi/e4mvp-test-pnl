# Requirements: Factory P&L Panel

## Core Value
A single factory admin records revenue, production costs and expenses (by hand or by Excel upload) and sees correct Gross, Operating and Net Profit in OMR for any day or month range, with charts and reports to export.

## Personas & Roles
- **Admin (only user)**: one account, email + password. There is no signup page and no other roles. The admin account is created by seed/env config.

## Features
| id | feature | persona | phase |
|---|---|---|---|
| F-1 | Single admin login (email + password), logout, no signup page | Admin | 1 |
| F-2 | Manual entry (add / edit / delete / list) for every Revenue category: Sales (customer, product, qty, unit price, date), Sales returns (reference, amount, date), Other income (description, amount, date) | Admin | 1 |
| F-3 | Manual entry for every COGS category: Raw material purchases (supplier, material, qty, unit cost, date), Raw material consumption (material, qty used, production run, date), Direct labour (description, hours, rate/hour, date), Machine running cost (description, amount, production run, date), Finished goods produced (product, qty, total production cost, date) | Admin | 1 |
| F-4 | Manual entry for every Operating Expense category: Salaries (department, amount, month), Utilities (type electricity/water/gas, amount, month), Rent (amount, month), Maintenance & repairs, Transportation & logistics, Marketing & sales, Admin & office (each description, amount, date) | Admin | 1 |
| F-5 | Manual entry for every Other category: Depreciation (asset name, monthly charge, month), Loan interest (description, amount, month), Tax provision (description, amount, month) | Admin | 1 |
| F-6 | P&L engine: Net Revenue, COGS, Gross / Operating / Net Profit, using the confirmed rules in Edge Cases | Admin | 1 |
| F-7 | Dashboard: current month total revenue, COGS, operating expenses, gross profit, net profit, plus a 12-month trend chart | Admin | 1 |
| F-8 | Reports with a date range filter and a Daily/Monthly toggle: Gross Profit, Operating Profit, Net Profit, P&L summary table, expense breakdown bar chart, revenue vs cost line chart, cost per unit produced | Admin | 1 |
| F-9 | Sample data (several months) plus a one-click "Clear sample data" that removes all of it | Admin | 1 |
| F-10 | Downloadable Excel template for each of the 18 categories | Admin | 2 |
| F-11 | Excel upload per category: preview first, then confirm; invalid rows are flagged and skipped, with an error summary | Admin | 2 |
| F-12 | Export every report to Excel | Admin | 2 |
| F-13 | Export every report to PDF | Admin | 2 |
| F-14 | One-click month-end accountant pack: pick a month and get the P&L summary, expense breakdown and cost per unit in one PDF and one Excel file (user approved) | Admin | 2 |

## Phases
- **Phase 1 (MVP)**: enter data by hand and see correct profit on the dashboard and reports → F-1..F-9. [requirement](phase1/requirement.md) · [journeys](phase1/journeys.md)
- **Phase 2**: bulk Excel import, report exports and month-end accountant pack → F-10..F-14.

## UI/UX Rules
- Clean, professional finance panel: left sidebar (Dashboard, Data Entry grouped by Revenue / COGS / Operating Expenses / Other, Reports, Settings), white cards, one restrained accent colour, green for profit and red for loss.
- Every amount is shown as `OMR 1,234.567`: always 3 decimals (baisa). Losses are shown with a minus sign in red.
- Desktop first; works on a laptop screen (1280px and up) and stays usable on a tablet.
- Dates are shown as DD MMM YYYY. Business timezone is Asia/Muscat.

## Integrations
- None external. JWT email/password auth for the single admin. Charts and Excel/PDF are built with in-app libraries.

## Edge Cases
- **Net Revenue** = Sales (qty × unit price) + Other income − Sales returns.
- **COGS** = Raw material consumed (valued) + Direct labour (hours × rate) + Machine running cost. Raw material *purchases* do NOT count as cost; they only set the material's average cost. Finished goods produced do NOT add to COGS.
- **Consumption valuation**: qty used × the weighted average unit cost of that material, from all purchases of it dated on or before the consumption date. Material names match case-insensitively with spaces trimmed. If no purchase exists yet, the line is valued at 0 and shown with a "No purchase cost found" warning.
- **Gross Profit** = Net Revenue − COGS. **Operating Profit** = Gross Profit − Operating Expenses. **Net Profit** = Operating Profit − Other (depreciation + loan interest + tax provision).
- **Monthly items** (salaries, utilities, rent, depreciation, loan interest, tax provision): in the daily view the amount is spread evenly across the days of that month. In monthly totals it counts in full. In ranges that cover only part of a month, only the days inside the range count.
- **Dashboard month-to-date (user request after Phase 1):** the Dashboard's current-month cards cover the 1st of the month through today (Asia/Muscat). Monthly items count only the elapsed days' share (days elapsed including today ÷ days in month, using the same per-day spreading as the daily view). Dated records after today are excluded. The current-month point on the 12-month trend uses the same month-to-date figures, and past months stay in full. Reports are unchanged.
- **Cost per unit produced** = total production cost ÷ quantity from finished goods entries in the range, per product and overall. Division by zero shows "—".
- All money is held and rounded to 3 decimals. Quantities, prices and amounts must be greater than 0 (hours and rate too). Required fields cannot be empty.
- Empty ranges show zeros and an empty-state message, never an error.

## Seed Data
- One admin account (credentials in /app/memory/test_credentials.md).
- About 6 months of realistic sample records across all 18 categories for a small Omani factory, all marked as sample.
- Settings has "Clear sample data". After a confirmation it deletes every sample record in one click and leaves records the admin entered.
