import { BookSearchResult } from "../../../types/bookSearch";
import {
  BookSearchProvider,
  BookSearchQuery,
  BookSearchRateLimitError,
} from "../provider";
import { isIsbn13, normalizeIsbn } from "../normalizers/isbn";

export class CompositeBookSearchProvider implements BookSearchProvider {
  constructor(
    private readonly googleBooks: BookSearchProvider,
    private readonly openBd: BookSearchProvider
  ) {}

  async search(query: BookSearchQuery): Promise<BookSearchResult[]> {
    const keyword = query.keyword.trim();
    if (isIsbn13(keyword)) {
      const book = await this.findByIsbn13(keyword);
      return book ? [book] : [];
    }

    return this.googleBooks.search(query);
  }

  async findByIsbn13(isbn13: string): Promise<BookSearchResult | null> {
    const normalized = normalizeIsbn(isbn13);
    const googleBook = await this.findGoogleBook(normalized);
    const openBdBook = await this.openBd.findByIsbn13(normalized);

    if (googleBook && openBdBook) {
      return mergeBookSearchResult(googleBook, openBdBook);
    }
    return openBdBook ?? googleBook;
  }

  private async findGoogleBook(
    isbn13: string
  ): Promise<BookSearchResult | null> {
    try {
      return await this.googleBooks.findByIsbn13(isbn13);
    } catch (error: unknown) {
      if (error instanceof BookSearchRateLimitError) {
        return null;
      }
      throw error;
    }
  }
}

const mergeBookSearchResult = (
  googleBook: BookSearchResult,
  openBdBook: BookSearchResult
): BookSearchResult => {
  return {
    ...googleBook,
    source: "openbd",
    sourceId: openBdBook.sourceId,
    title: preferText(openBdBook.title, googleBook.title, ["タイトル不明"]),
    authors: preferAuthors(openBdBook.authors, googleBook.authors),
    publisher: preferText(openBdBook.publisher, googleBook.publisher, ["不明"]),
    publishedAt: preferDate(openBdBook.publishedAt, googleBook.publishedAt),
    imageUrl: preferImageUrl(openBdBook.imageUrl, googleBook.imageUrl),
    description: googleBook.description,
  };
};

const preferText = (
  primary: string,
  fallback: string,
  invalidValues: string[]
): string => {
  const trimmed = primary.trim();
  if (!trimmed || invalidValues.includes(trimmed)) {
    return fallback;
  }
  return trimmed;
};

const preferAuthors = (
  primary: string[],
  fallback: string[]
): string[] => {
  const valid = primary.filter((author) => author && author !== "著者不明");
  return valid.length > 0 ? valid : fallback;
};

const preferDate = (primary: Date, fallback: Date): Date => {
  if (primary.getFullYear() === 1970) {
    return fallback;
  }
  return primary;
};

const preferImageUrl = (
  primary: string | null,
  fallback: string | null
): string | null => {
  return primary || fallback;
};
