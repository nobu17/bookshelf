type SupportedDateFormat = "YYYY-MM-DD";
// | 'YYYY年M月D日(曜)';

export function toDate(
  str: string,
  format: SupportedDateFormat = "YYYY-MM-DD"
): Date {
  switch (format) {
    case "YYYY-MM-DD":
      return new Date(str);
    default:
      throw new Error(`Unsupported format: ${format}`);
  }
}

// return as "YYYY-MM-DD"
export function dateToString(date: Date): string {
  const formattedDate = new Intl.DateTimeFormat("ja-JP", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  }).format(date).replace(/\//g, "-");
  return formattedDate;
}
