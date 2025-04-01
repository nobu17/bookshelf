export const getImageUrl = (isbn13: string): string => {
  return `https://ndlsearch.ndl.go.jp/thumbnail/${isbn13}.jpg`;
};

export const getFallbackImageUrl = (baseUrl: string = ""): string => {
  return `${baseUrl}/images/no_image.jpg`;
};
