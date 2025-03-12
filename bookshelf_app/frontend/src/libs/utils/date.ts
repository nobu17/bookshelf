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
  })
    .format(date)
    .replace(/\//g, "-");
  return formattedDate;
}

// return as "YYYY-MM-DD hh:mm"
export function dateTimeToString(date: Date): string {
  const formattedDate = new Intl.DateTimeFormat("ja-JP", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  })
    .format(date)
    .replace(/\//g, "-");
  return formattedDate;
}

export const toISOStringWithTimezone = (date: Date): string => {
  const year = date.getFullYear().toString();
  const month = zeroPadding((date.getMonth() + 1).toString());
  const day = zeroPadding(date.getDate().toString());

  const hour = zeroPadding(date.getHours().toString());
  const minute = zeroPadding(date.getMinutes().toString());
  const second = zeroPadding(date.getSeconds().toString());

  const localDate = `${year}-${month}-${day}`;
  const localTime = `${hour}:${minute}:${second}`;

  const diffFromUtc = date.getTimezoneOffset();

  // UTCだった場合
  if (diffFromUtc === 0) {
    const tzSign = "Z";
    return `${localDate}T${localTime}${tzSign}`;
  }

  // UTCではない場合
  const tzSign = diffFromUtc < 0 ? "+" : "-";
  const tzHour = zeroPadding((Math.abs(diffFromUtc) / 60).toString());
  const tzMinute = zeroPadding((Math.abs(diffFromUtc) % 60).toString());

  return `${localDate}T${localTime}${tzSign}${tzHour}:${tzMinute}`;
};

const zeroPadding = (s: string): string => {
  return ("0" + s).slice(-2);
};
