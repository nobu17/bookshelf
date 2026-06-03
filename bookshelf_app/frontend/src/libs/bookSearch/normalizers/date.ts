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
  if (/^\d{6}$/.test(value)) {
    const year = Number(value.slice(0, 4));
    const month = Number(value.slice(4, 6));
    return new Date(year, month - 1, 1);
  }
  if (/^\d{8}$/.test(value)) {
    const year = Number(value.slice(0, 4));
    const month = Number(value.slice(4, 6));
    const day = Number(value.slice(6, 8));
    return new Date(year, month - 1, day);
  }

  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) {
    return new Date(1970, 0, 1);
  }
  return parsed;
};
