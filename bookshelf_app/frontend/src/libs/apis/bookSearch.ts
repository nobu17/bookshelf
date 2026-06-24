import { BookSearchResult } from "../../types/bookSearch";
import { toDate } from "../utils/date";
import ApiBase, { ApiResponse } from "./apibase";

export default class BookSearchApi extends ApiBase {
  async search(keyword: string): Promise<ApiResponse<BookSearchResponse>> {
    const res = await this.getAsync<ApiBookSearchResponse>(
      `/book_search?keyword=${encodeURIComponent(keyword)}`
    );
    return { data: convert(res.data) };
  }

  async searchPublisherBooks(
    publisherId: string,
    keyword = "",
    limit = 40
  ): Promise<ApiResponse<BookSearchResponse>> {
    const params = new URLSearchParams({ limit: String(limit) });
    if (keyword.trim()) {
      params.set("keyword", keyword.trim());
    }
    const res = await this.getAsync<ApiBookSearchResponse>(
      `/book_search/publishers/${encodeURIComponent(
        publisherId
      )}/books?${params.toString()}`
    );
    return { data: convert(res.data) };
  }

  async findDescriptionByIsbn13(
    isbn13: string
  ): Promise<ApiResponse<BookDescriptionResponse>> {
    const res = await this.getAsync<ApiBookDescriptionResponse>(
      `/book_search/isbn13/${encodeURIComponent(isbn13)}/description`
    );
    return {
      data: {
        isbn13: res.data.isbn13,
        description: res.data.description ?? null,
      },
    };
  }
}

type BookSearchResponse = {
  books: BookSearchResult[];
};

type ApiBookSearchResponse = {
  books: ApiBookSearchResult[];
};

type ApiBookSearchResult = {
  source: string;
  source_id: string;
  title: string;
  authors: string[];
  publisher: string;
  isbn13: string;
  published_at: string;
  image_url: string | null;
  description?: string | null;
};

type BookDescriptionResponse = {
  isbn13: string;
  description: string | null;
};

type ApiBookDescriptionResponse = {
  isbn13: string;
  description?: string | null;
};

const convert = (data: ApiBookSearchResponse): BookSearchResponse => {
  return {
    books: data.books.map((book) => ({
      source:
        book.source === "openbd"
          ? "openbd"
          : book.source === "publisher-catalog"
          ? "publisher-catalog"
          : "google-books",
      sourceId: book.source_id,
      title: book.title,
      authors: book.authors,
      publisher: book.publisher,
      isbn13: book.isbn13,
      publishedAt: toDate(book.published_at),
      imageUrl: book.image_url,
      description: book.description ?? undefined,
    })),
  };
};
