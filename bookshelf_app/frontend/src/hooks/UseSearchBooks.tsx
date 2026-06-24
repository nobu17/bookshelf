import { useState } from "react";
import {
  BookSearchResult,
  BookSearchResultWithReviews,
} from "../types/bookSearch";
import { BookWithMyReviewsApi } from "../libs/apis/bookWithReviews";
import useAuthApi from "./UseAuthApi";
import { BookWithReviews } from "../types/data";
import BookSearchApi from "../libs/apis/bookSearch";
import { toError } from "../libs/utils/error";

const api = new BookWithMyReviewsApi();
const bookSearchApi = new BookSearchApi();

export default function useSearchBooks() {
  useAuthApi(api);
  const [reviews, setReviews] = useState<BookWithReviews[] | null>(null);
  const [books, setBooks] = useState<BookSearchResultWithReviews[]>([]);
  const [error, setError] = useState<Error>();
  const [loading, setLoading] = useState(false);

  const search = async (searchWord: string) => {
    try {
      setError(undefined);
      setLoading(true);
      const myReviews = await loadMyReviewsForSearch(reviews, setReviews);
      const res = (await bookSearchApi.search(searchWord)).data.books;
      setBooks(sortBooks(aggregateReview(res, myReviews)));
    } catch (e: unknown) {
      setError(toError(e));
    } finally {
      setLoading(false);
    }
  };

  const searchPublisher = async (publisherId: string, keyword = "") => {
    try {
      setError(undefined);
      setLoading(true);
      const myReviews = await loadMyReviewsForSearch(reviews, setReviews);
      const res = (
        await bookSearchApi.searchPublisherBooks(publisherId, keyword)
      ).data.books;
      setBooks(sortBooks(aggregateReview(res, myReviews)));
    } catch (e: unknown) {
      setError(toError(e));
    } finally {
      setLoading(false);
    }
  };

  const reload = async (searchWord: string) => {
    try {
      setError(undefined);
      setLoading(true);
      const myReviews = (await api.getMyReviews()).data.books_with_reviews;
      setReviews(myReviews);
      const res = (await bookSearchApi.search(searchWord)).data.books;
      setBooks(sortBooks(aggregateReview(res, myReviews)));
    } catch (e: unknown) {
      setError(toError(e));
    } finally {
      setLoading(false);
    }
  };

  return {
    error,
    loading,
    books,
    search,
    searchPublisher,
    reload,
  };
}

const sortBooks = (
  books: BookSearchResultWithReviews[]
): BookSearchResultWithReviews[] => {
  return books.sort((a, b) => b.publishedAt.getTime() - a.publishedAt.getTime());
};

const loadMyReviewsForSearch = async (
  reviews: BookWithReviews[] | null,
  setReviews: (reviews: BookWithReviews[]) => void
): Promise<BookWithReviews[]> => {
  if (reviews != null) {
    return reviews;
  }
  const myReviews = (await api.getMyReviewsForEdit()).data.books_with_reviews;
  setReviews(myReviews);
  return myReviews;
};

const aggregateReview = (
  books: BookSearchResult[],
  reviews: BookWithReviews[] | null
): BookSearchResultWithReviews[] => {
  const aggregates: BookSearchResultWithReviews[] = [];
  for (const book of books) {
    const base: BookSearchResultWithReviews = { ...book, bookId: "", reviews: [] };
    if (reviews) {
      const sameBook = reviews.find((x) => x.isbn13 === base.isbn13);
      if (sameBook) {
        base.bookId = sameBook.bookId;
        base.reviews = sameBook.reviews;
      }
    }

    aggregates.push(base);
  }

  return aggregates;
};
