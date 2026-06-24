import { Review } from "./data";

export type BookSearchSource = "google-books" | "openbd" | "publisher-catalog";

export type BookSearchResult = {
  source: BookSearchSource;
  sourceId: string;
  title: string;
  authors: string[];
  publisher: string;
  isbn13: string;
  publishedAt: Date;
  imageUrl: string | null;
  description?: string;
};

export type BookSearchResultWithReviews = BookSearchResult & {
  bookId: string;
  reviews: Review[];
};
