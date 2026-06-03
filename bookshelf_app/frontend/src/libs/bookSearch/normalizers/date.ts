export const parsePublishedDate = (value: string | undefined): Date => {
  if (!value) {
    return new Date(1970, 0, 1);
  }

  if (/^\d{4}$/.test(value)) {
    return new Date(Number(value), 0, 1);
  }
  if (/^\d{4}-\d{2}$/.test(value)) {
    const [year, month] = value.split("-").map(Number);
    return new Date(year, month - 1, 1);
  }
  if (/^\d{4}-\d{2}-\d{2}$/.test(value)) {
    const [year, month, day] = value.split("-").map(Number);
    return new Date(year, month - 1, day);
  }

  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) {
    return new Date(1970, 0, 1);
  }
  return parsed;
};
