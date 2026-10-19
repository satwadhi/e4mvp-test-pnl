const NUMERIC = ["money", "quantity"];

export function validateRecord(fields, values) {
  const errors = {};
  fields.forEach((f) => {
    const raw = values[f.key];
    const s = raw == null ? "" : String(raw).trim();
    if (s === "") {
      errors[f.key] = "Required";
      return;
    }
    if (NUMERIC.includes(f.type)) {
      const n = Number(s);
      if (!Number.isFinite(n)) errors[f.key] = "Must be a number";
      else if (Math.round(n * 1000) <= 0) errors[f.key] = "Must be greater than 0";
    }
  });
  return errors;
}

export const isNumericField = (f) => NUMERIC.includes(f.type);
