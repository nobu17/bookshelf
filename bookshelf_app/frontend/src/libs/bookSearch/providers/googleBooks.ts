import axios from "axios";

import { BookSearchResult } from "../../../types/bookSearch";
import { BookSearchProvider, BookSearchQuery } from "../provider";
import {
  convertIsbn10ToIsbn13,
  isIsbn13,
  normalizeIsbn,
} from "../normalizers/isbn";
import { parsePublishedDate } from "../normalizers/date";

const ApiRoot = "https://www.googleapis.com/books/v1/volumes";
const MaxResults = 40;
const GoogleBooksApiKey = import.meta.env.VITE_GOOGLE_BOOKS_API_KEY;

export class GoogleBooksProvider implements BookSearchProvider {
  async search(query: BookSearchQuery): Promise<BookSearchResult[]> {
    const keyword = query.keyword.trim();
    if (!keyword) {
      return [];
    }

    const q = isIsbn13(keyword) ? `isbn:${normalizeIsbn(keyword)}` : keyword;
    const response = await axios.get<GoogleVolumesResponse>(ApiRoot, {
      params: {
        q,
        printType: "books",
        langRestrict: "ja",
        maxResults: Math.min(query.maxResults ?? MaxResults, MaxResults),
        key: GoogleBooksApiKey || undefined,
      },
    });

    return uniqueByIsbn13(
      (response.data.items ?? [])
        .map(convertVolume)
        .filter((book): book is BookSearchResult => book !== null)
    );
  }

  async findByIsbn13(isbn13: string): Promise<BookSearchResult | null> {
    const results = await this.search({
      keyword: normalizeIsbn(isbn13),
      maxResults: 1,
    });
    return results[0] ?? null;
  }
}

const convertVolume = (volume: GoogleVolume): BookSearchResult | null => {
  const info = volume.volumeInfo;
  if (!info) {
    return null;
  }

  const isbn13 = findIsbn13(info.industryIdentifiers ?? []);
  if (!isbn13) {
    return null;
  }

  return {
    source: "google-books",
    sourceId: volume.id,
    title: info.title || "タイトル不明",
    authors: info.authors && info.authors.length > 0 ? info.authors : ["著者不明"],
    publisher: info.publisher || "不明",
    isbn13,
    publishedAt: parsePublishedDate(info.publishedDate),
    imageUrl:
      info.imageLinks?.thumbnail ??
      info.imageLinks?.smallThumbnail ??
      null,
    description: info.description,
  };
};

const findIsbn13 = (
  identifiers: GoogleIndustryIdentifier[]
): string | null => {
  const isbn13 = identifiers.find((item) => item.type === "ISBN_13");
  if (isbn13) {
    return normalizeIsbn(isbn13.identifier);
  }

  const isbn10 = identifiers.find((item) => item.type === "ISBN_10");
  if (isbn10) {
    return convertIsbn10ToIsbn13(isbn10.identifier);
  }

  return null;
};

const uniqueByIsbn13 = (books: BookSearchResult[]): BookSearchResult[] => {
  const exists = new Set<string>();
  const results: BookSearchResult[] = [];
  for (const book of books) {
    if (exists.has(book.isbn13)) {
      continue;
    }
    exists.add(book.isbn13);
    results.push(book);
  }
  return results;
};

type GoogleVolumesResponse = {
  items?: GoogleVolume[];
};

type GoogleVolume = {
  id: string;
  volumeInfo?: GoogleVolumeInfo;
};

type GoogleVolumeInfo = {
  title?: string;
  authors?: string[];
  publisher?: string;
  publishedDate?: string;
  description?: string;
  industryIdentifiers?: GoogleIndustryIdentifier[];
  imageLinks?: {
    smallThumbnail?: string;
    thumbnail?: string;
  };
};

type GoogleIndustryIdentifier = {
  type: string;
  identifier: string;
};
