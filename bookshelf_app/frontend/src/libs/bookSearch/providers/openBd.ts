import axios from "axios";

import { BookSearchResult } from "../../../types/bookSearch";
import { BookSearchProvider, BookSearchQuery } from "../provider";
import { isIsbn13, normalizeIsbn } from "../normalizers/isbn";
import { parsePublishedDate } from "../normalizers/date";

const ApiRoot = "https://api.openbd.jp/v1/get";

export class OpenBdProvider implements BookSearchProvider {
  async search(query: BookSearchQuery): Promise<BookSearchResult[]> {
    const keyword = query.keyword.trim();
    if (!isIsbn13(keyword)) {
      return [];
    }

    const book = await this.findByIsbn13(keyword);
    return book ? [book] : [];
  }

  async findByIsbn13(isbn13: string): Promise<BookSearchResult | null> {
    const normalized = normalizeIsbn(isbn13);
    const response = await axios.get<OpenBdBookResponse[]>(ApiRoot, {
      params: { isbn: normalized },
    });
    const item = response.data[0];
    if (!item?.summary) {
      return null;
    }

    const summary = item.summary;
    return {
      source: "openbd",
      sourceId: normalized,
      title: summary.title || "タイトル不明",
      authors: summary.author ? splitAuthors(summary.author) : ["著者不明"],
      publisher: summary.publisher || "不明",
      isbn13: normalizeIsbn(summary.isbn || normalized),
      publishedAt: parsePublishedDate(summary.pubdate),
      imageUrl: normalizeCoverUrl(summary.cover),
    };
  }
}

const splitAuthors = (author: string): string[] => {
  const authors = author
    .split(/[、,／/]/)
    .map((item) => item.trim())
    .filter((item) => item.length > 0);
  return authors.length > 0 ? authors : ["著者不明"];
};

const normalizeCoverUrl = (cover: string | undefined): string | null => {
  if (!cover) {
    return null;
  }
  return cover.replace(/^http:\/\//, "https://");
};

type OpenBdBookResponse = {
  summary?: {
    isbn?: string;
    title?: string;
    volume?: string;
    series?: string;
    publisher?: string;
    pubdate?: string;
    cover?: string;
    author?: string;
  };
} | null;
