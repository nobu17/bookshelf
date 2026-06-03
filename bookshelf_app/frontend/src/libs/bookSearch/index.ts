import { GoogleBooksProvider } from "./providers/googleBooks";
import { BookSearchProvider, BookSearchQuery } from "./provider";
import { BookSearchResult } from "../../types/bookSearch";

const provider: BookSearchProvider = new GoogleBooksProvider();

export const searchBooks = async (
  keyword: string
): Promise<BookSearchResult[]> => {
  const query: BookSearchQuery = { keyword };
  return provider.search(query);
};

export const findBookByIsbn13 = (isbn13: string) => {
  return provider.findByIsbn13(isbn13);
};
