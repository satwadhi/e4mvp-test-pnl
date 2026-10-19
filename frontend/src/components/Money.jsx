import { cn } from "@/lib/utils";
import { formatOMR, isNegative } from "@/lib/format";

export function Money({ value, signed = false, className, ...props }) {
  const neg = isNegative(value);
  const color = signed ? (neg ? "text-rose-600" : "text-emerald-600") : neg ? "text-rose-600" : "";
  return (
    <span className={cn("num whitespace-nowrap", className, color)} {...props}>
      {formatOMR(value)}
    </span>
  );
}
