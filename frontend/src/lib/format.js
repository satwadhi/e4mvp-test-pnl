const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
const omrFmt = new Intl.NumberFormat("en-US", { minimumFractionDigits: 3, maximumFractionDigits: 3 });
const qtyFmt = new Intl.NumberFormat("en-US", { maximumFractionDigits: 3 });
const compactFmt = new Intl.NumberFormat("en-US", { notation: "compact", maximumFractionDigits: 1 });

export function formatOMR(value) {
  const baisa = Math.round(Number(value || 0) * 1000);
  const abs = omrFmt.format(Math.abs(baisa) / 1000);
  return baisa < 0 ? `-OMR ${abs}` : `OMR ${abs}`;
}

export const isNegative = (value) => Math.round(Number(value || 0) * 1000) < 0;
export const formatQty = (value) => qtyFmt.format(Number(value || 0));
export const formatCompact = (value) => compactFmt.format(Number(value || 0));

export function formatDate(iso) {
  if (!iso) return "";
  const [y, m, d] = iso.split("-");
  return `${d} ${MONTHS[Number(m) - 1]} ${y}`;
}

export function formatMonth(key) {
  if (!key) return "";
  const [y, m] = key.split("-");
  return `${MONTHS[Number(m) - 1]} ${y}`;
}

export function todayMuscat() {
  return new Intl.DateTimeFormat("en-CA", { timeZone: "Asia/Muscat" }).format(new Date());
}

export function addMonths(iso, delta) {
  const [y, m] = iso.split("-").map(Number);
  const d = new Date(Date.UTC(y, m - 1 + delta, 1));
  return d.toISOString().slice(0, 10);
}

export function endOfMonth(iso) {
  const [y, m] = iso.split("-").map(Number);
  return new Date(Date.UTC(y, m, 0)).toISOString().slice(0, 10);
}
