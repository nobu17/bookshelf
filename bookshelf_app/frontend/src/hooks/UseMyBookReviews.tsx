import { useEffect, useState } from "react";
import { BookWithMyReviewsApi } from "../libs/apis/bookWithReviews";
import { BookWithReviews, Review } from "../types/data";
import { ApiError } from "../libs/apis/apibase";
import useAuthApi from "./UseAuthApi";
import ReviewsApi from "../libs/apis/reviews";

const api = new BookWithMyReviewsApi();
const reviewApi = new ReviewsApi();

export default function useMyBookReviews() {
  useAuthApi(api);
  useAuthApi(reviewApi);
  const [bookWithReviews, setBookWithReviews] = useState<BookWithReviews[]>([]);
  const [error, setError] = useState<Error>();
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const init = async () => {
      await loadAsync();
    };
    init();
  }, []);

  const loadAsync = async () => {
    setLoading(true);
    try {
      const res = await api.getMyReviews();
      setBookWithReviews(res.data.books_with_reviews);
    } catch (e: unknown) {
      if (e instanceof ApiError) {
        if (!e.isBadRequest()) {
          setError(e);
          return;
        }
      } else if (e instanceof Error) {
        setError(e);
        return;
      }
      setError(new Error("unexpected error."));
    } finally {
      setLoading(false);
    }
  };

  const updateAsync = async (reviewId: string, review: Review) => {
    setLoading(true);
    try {
      await reviewApi.updateReview(reviewId, review);
    } catch (e: unknown) {
      if (e instanceof ApiError) {
        if (!e.isBadRequest()) {
          setError(e);
          return;
        }
      } else if (e instanceof Error) {
        setError(e);
        return;
      }
      setError(new Error("unexpected error."));
    } finally {
      setLoading(false);
    }
    await loadAsync();
  };

  return {
    bookWithReviews,
    error,
    loading,
    loadAsync,
    updateAsync,
  };
}
