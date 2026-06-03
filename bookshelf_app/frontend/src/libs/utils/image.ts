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
