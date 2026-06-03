import { BookSearchResult } from "../../../types/bookSearch";
import { BookSearchProvider, BookSearchQuery } from "../provider";

export class OpenBdProvider implements BookSearchProvider {
  async search(query: BookSearchQuery): Promise<BookSearchResult[]> {
    void query;
    return [];
  }

  async findByIsbn13(isbn13: string): Promise<BookSearchResult | null> {
    void isbn13;
    return null;
  }
}
