import { useState } from "react";
import { searchNdlBooks } from "../libs/apis/bookSearch";
import { NdlBook, NdlBookWithReviews } from "../types/ndls";
import { BookWithMyReviewsApi } from "../libs/apis/bookWithReviews";
import useAuthApi from "./UseAuthApi";
import { BookWithReviews } from "../types/data";

const api = new BookWithMyReviewsApi();

export default function useSearchBooks() {
  useAuthApi(api);
  const [reviews, setReviews] = useState<BookWithReviews[] | null>(null);
  const [books, setBooks] = useState<NdlBookWithReviews[]>([]);
  const [error, setError] = useState<Error>();
  const [loading, setLoading] = useState(false);

  const search = async (searchWord: string) => {
    try {
      setError(undefined);
      setLoading(true);
      let myReviews: BookWithReviews[] = [];
      if (reviews == null) {
        myReviews = (await api.getMyReviews()).data.books_with_reviews;
        setReviews(myReviews);
      }
      const res = await searchNdlBooks(searchWord);
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
      const res = await searchNdlBooks(searchWord);
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
  books: NdlBook[],
  reviews: BookWithReviews[] | null
): NdlBookWithReviews[] => {
  const aggregates: NdlBookWithReviews[] = [];
  for (const book of books) {
    const base: NdlBookWithReviews = { ...book, reviews: [] };
    if (reviews) {
      const sameBook = reviews.find((x) => x.isbn13 === base.isbn13);
      if (sameBook) {
        base.reviews = sameBook.reviews;
      }
    }

    aggregates.push(base);
  }

  return aggregates;
};
