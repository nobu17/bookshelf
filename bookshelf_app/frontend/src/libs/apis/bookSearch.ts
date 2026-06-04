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

const convert = (data: ApiBookSearchResponse): BookSearchResponse => {
  return {
    books: data.books.map((book) => ({
      source: book.source === "openbd" ? "openbd" : "google-books",
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
