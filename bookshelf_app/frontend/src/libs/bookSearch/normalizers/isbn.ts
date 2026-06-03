export const normalizeIsbn = (isbn: string): string => {
  return isbn.replace(/[-\s]/g, "").toUpperCase();
};

export const isIsbn13 = (value: string): boolean => {
  return /^\d{13}$/.test(normalizeIsbn(value));
};

export const convertIsbn10ToIsbn13 = (isbn10: string): string | null => {
  const normalized = normalizeIsbn(isbn10);
  if (!/^\d{9}[\dX]$/.test(normalized)) {
    return null;
  }

  const isbnBase = `978${normalized.slice(0, 9)}`;
  const digits = isbnBase.split("").map(Number);
  const checkDigit =
    (10 -
      (digits.reduce(
        (sum, num, idx) => sum + num * (idx % 2 === 0 ? 1 : 3),
        0
      ) %
        10)) %
    10;

  return `${isbnBase}${checkDigit}`;
};
