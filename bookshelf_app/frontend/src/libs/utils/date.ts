type SupportedDateFormat = "YYYY-MM-DD";
// | 'YYYY年M月D日(曜)';

export function toDate(str: string, format: SupportedDateFormat): Date {
  switch (format) {
    case "YYYY-MM-DD":
      return new Date(str);
    default:
      throw new Error(`Unsupported format: ${format}`);
  }
}
