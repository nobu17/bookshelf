import { useState } from "react";
import { searchBooks } from "../libs/bookSearch";
import {
  BookSearchResult,
  BookSearchResultWithReviews,
} from "../types/bookSearch";
import { BookWithMyReviewsApi } from "../libs/apis/bookWithReviews";
import useAuthApi from "./UseAuthApi";
import { BookWithReviews } from "../types/data";

const api = new BookWithMyReviewsApi();

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
      let myReviews: BookWithReviews[] = [];
      if (reviews == null) {
        myReviews = (await api.getMyReviewsForEdit()).data.books_with_reviews;
        setReviews(myReviews);
      }
      const res = await searchBooks(searchWord);
      const aggregated = aggregateReview(res, myReviews);
      aggregated.sort(
        (a, b) => b.publishedAt.getTime() - a.publishedAt.getTime()
      );
      setBooks(aggregated);
    } catch (e: unknown) {
      if (e instanceof Error) {
        setError(e);
        return;
      }
      setError(new Error("Unexpected error:" + typeof e));
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
      const res = await searchBooks(searchWord);
      const aggregated = aggregateReview(res, myReviews);
      aggregated.sort(
        (a, b) => b.publishedAt.getTime() - a.publishedAt.getTime()
      );
      setBooks(aggregated);
    } catch (e: unknown) {
      if (e instanceof Error) {
        setError(e);
        return;
      }
      setError(new Error("Unexpected error:" + typeof e));
    } finally {
      setLoading(false);
    }
  };

  return {
    error,
    loading,
    books,
    search,
    reload,
  };
}

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
