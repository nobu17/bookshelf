import { BookSearchResult } from "../../types/bookSearch";

export type BookSearchQuery = {
  keyword: string;
  maxResults?: number;
};

export interface BookSearchProvider {
  search(query: BookSearchQuery): Promise<BookSearchResult[]>;
  findByIsbn13(isbn13: string): Promise<BookSearchResult | null>;
}

export class BookSearchRateLimitError extends Error {
  constructor() {
    super("外部書籍検索APIの利用制限に達しました。しばらく時間を置いてから再度お試しください。");
    this.name = "BookSearchRateLimitError";
  }
}
