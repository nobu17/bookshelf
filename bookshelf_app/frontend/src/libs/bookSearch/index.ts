import { CompositeBookSearchProvider } from "./providers/composite";
import { GoogleBooksProvider } from "./providers/googleBooks";
import { OpenBdProvider } from "./providers/openBd";
import { BookSearchProvider, BookSearchQuery } from "./provider";
import { BookSearchResult } from "../../types/bookSearch";

const provider: BookSearchProvider = new CompositeBookSearchProvider(
  new GoogleBooksProvider(),
  new OpenBdProvider()
);

export const searchBooks = async (
  keyword: string
): Promise<BookSearchResult[]> => {
  const query: BookSearchQuery = { keyword };
  return provider.search(query);
};

export const findBookByIsbn13 = (isbn13: string) => {
  return provider.findByIsbn13(isbn13);
};
