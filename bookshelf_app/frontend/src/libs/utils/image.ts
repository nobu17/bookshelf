type BookImageSource = {
  isbn13: string;
  imageUrl?: string | null;
};

export const getImageUrl = (isbn13: string): string => {
  void isbn13;
  return getFallbackImageUrl();
};

export const getBookInfoImageUrl = (book: BookImageSource): string => {
  return book.imageUrl || getFallbackImageUrl();
};

export const getSearchResultImageUrl = (book: BookImageSource): string => {
  return getBookInfoImageUrl(book);
};

export const getFallbackImageUrl = (baseUrl: string = ""): string => {
  return `${baseUrl}/images/no_image.jpg`;
};

export const isGoogleBooksImageUrl = (imageUrl?: string | null): boolean => {
  if (!imageUrl) {
    return false;
  }

  try {
    const url = new URL(imageUrl);
    return ["books.google.com", "books.google.co.jp"].includes(
      url.hostname.toLowerCase()
    );
  } catch {
    return false;
  }
};
