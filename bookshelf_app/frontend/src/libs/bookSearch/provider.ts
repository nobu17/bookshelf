import { BookSearchResult } from "../../types/bookSearch";

export type BookSearchQuery = {
  keyword: string;
  maxResults?: number;
};

export interface BookSearchProvider {
  search(query: BookSearchQuery): Promise<BookSearchResult[]>;
  findByIsbn13(isbn13: string): Promise<BookSearchResult | null>;
}
