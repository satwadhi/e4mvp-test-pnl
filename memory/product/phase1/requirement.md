# Phase 1 Requirement (phase-1): Manual entry → correct P&L

**Goal:** the admin logs in, enters records in any of the 18 categories by hand, and sees correct OMR figures on the dashboard and reports. Formulas and rules are in `../overview.md` (Edge Cases). Excel import and exports are Phase 2.

## Functional requirements
- REQ-1 [always] The system shall allow only one admin account, and shall show no signup page.
- REQ-2 [event] When the admin submits a correct email and password, the system shall open the Dashboard.
- REQ-3 [unwanted] If the email or password is wrong, then the system shall show "Invalid email or password".
- REQ-4 [unwanted] If a logged-out visitor opens any panel page or API, then the system shall redirect to Login (API returns 401).
- REQ-5 [event] When the admin clicks Logout, the system shall return to the Login page.
- REQ-6 [always] The system shall provide a data entry page for each of the 18 categories listed in overview F-2..F-5, with exactly the fields listed there.
- REQ-7 [event] When the admin saves a valid record, the system shall show it at the top of that category's list.
- REQ-8 [unwanted] If a required field is empty, then the system shall block saving and mark the field "Required".
- REQ-9 [unwanted] If a quantity, price, cost, hours, rate or amount is zero or negative, then the system shall block saving with "Must be greater than 0".
- REQ-10 [event] When the admin edits a record, the system shall update every total that depends on it.
- REQ-11 [event] When the admin confirms delete on a record, the system shall remove it from the list and from every total.
- REQ-12 [always] The system shall calculate computed line totals (sales = qty × unit price, purchases = qty × unit cost, labour = hours × rate) and show them in the list.
- REQ-13 [always] The system shall show Utilities type as a choice of Electricity, Water or Gas.
- REQ-14 [always] The system shall value raw material consumption at the weighted average purchase cost of that material up to the consumption date.
- REQ-15 [unwanted] If a consumed material has no earlier purchase, then the system shall value it at OMR 0.000 and show "No purchase cost found".
- REQ-16 [always] The system shall calculate Net Revenue, COGS, Gross Profit, Operating Profit and Net Profit with the formulas in overview Edge Cases.
- REQ-17 [always] The system shall show every amount as "OMR" with 3 decimals.
- REQ-18 [always] The Dashboard shall show current-month Total Revenue, Total COGS, Total Operating Expenses, Gross Profit and Net Profit.
- REQ-19 [always] The Dashboard shall show a revenue, cost and net profit trend chart for the last 12 months.
- REQ-20 [event] When the admin picks a date range and Daily or Monthly view on Reports, the system shall recalculate all report sections for that range.
- REQ-21 [unwanted] If the start date is after the end date, then the system shall show "Start date must be before end date" and not run the report.
- REQ-22 [always] Reports shall show a P&L summary table with one row per day or month: Net Revenue, COGS, Gross Profit, Operating Expenses, Operating Profit, Other, Net Profit, plus a Total row.
- REQ-23 [always] Reports shall show an expense breakdown bar chart by category.
- REQ-24 [always] Reports shall show a revenue vs cost line chart over the range.
- REQ-25 [always] Reports shall show cost per unit produced, per product and overall.
- REQ-26 [state] While Daily view is selected, the system shall spread monthly items evenly across the days of their month (interpreted: in partial-month ranges only the days inside the range count).
- REQ-27 [unwanted] If a range has no records, then the system shall show zeros and "No data for this period".
- REQ-28 [always] The system shall load sample data covering about 6 months across all 18 categories, with each record flagged as sample.
- REQ-29 [event] When the admin confirms "Clear sample data" in Settings, the system shall delete every sample record and keep records the admin entered.
- REQ-30 [always] The backend shall publish its API contract at /api/openapi.json.
- REQ-31 [always] The Dashboard current-month cards shall show month-to-date figures from the 1st through today (Asia/Muscat), with monthly items counted only for elapsed days (interpreted: added after Phase 1 at the user's request).
- REQ-32 [always] The Dashboard shall label the period as "Month to date: 1–<today> <Mon> <YYYY>".
- REQ-33 [unwanted] If a dated record in the current month falls after today, then the system shall exclude it from the Dashboard cards.

## Quality requirements
```
Q-1  Tag: Calc.Accuracy
     Scale: OMR difference between panel figures and a hand calculation on the seeded data
     Meter: tester recomputes Gross/Operating/Net for 2 months from the API records
     Must: 0.000 difference   Plan: 0.000 difference
Q-2  Tag: Reports.Speed
     Scale: seconds from Apply to report rendered for a 12-month range on seed data
     Meter: browser timing, 3 runs
     Must: 3s   Plan: 1s
Q-3  Tag: Data.Durability
     Scale: records lost after logout, login and page reload
     Meter: tester adds 3 records, reloads and re-logs
     Must: 0   Plan: 0
Q-4  Tag: Security.Access
     Scale: panel APIs reachable without a token
     Meter: curl every /api route without auth
     Must: 0   Plan: 0
Q-5  Tag: Usability.FirstEntry
     Scale: minutes for a first-time admin to add one sales record unaided
     Meter: human
     Must: 2 min   Plan: 30s (estimate)
Q-6  Tag: Display.Layout
     Scale: overflowing or cut-off tables or cards at 1280px and 1024px width
     Meter: screenshots
     Must: 0   Plan: 0
```
