export const getImageUrl = (isbn13: string): string => {
  return `https://ndlsearch.ndl.go.jp/thumbnail/${isbn13}.jpg`;
};
