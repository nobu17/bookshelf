import { useEffect, useState } from "react";
import { BookWithMyReviewsApi } from "../libs/apis/bookWithReviews";
import { BookWithReviews, Review } from "../types/data";
import { ApiError } from "../libs/apis/apibase";
import useAuthApi from "./UseAuthApi";
import ReviewsApi from "../libs/apis/reviews";
import { ReviewEditInfo } from "../components/parts/BookReviewEditForm";

const api = new BookWithMyReviewsApi();
const reviewApi = new ReviewsApi();

export default function useMySpecificBookReviews() {
  useAuthApi(api);
  useAuthApi(reviewApi);
  const [bookWithReviews, setBookWithReviews] =
    useState<BookWithReviews | null>(null);
  const [bookId, setBookId] = useState("");
  const [error, setError] = useState<Error>();
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const init = async () => {
      await loadAsync();
    };
    if (bookId) {
      init();
    }
  }, [bookId]);

  const createAsync = async (bookId: string, createReview: ReviewEditInfo) => {
    setLoading(true);
    try {
      // attach book Id to review
      const createReviewInfo = { ...createReview, bookId: bookId };
      await reviewApi.createReview(createReviewInfo);
      // reload
      const res = await api.getMyReviewForEditByBookId(bookId);
      setBookWithReviews(res.data);
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

  const loadAsync = async () => {
    setLoading(true);
    try {
      const res = await api.getMyReviewForEditByBookId(bookId);
      setBookWithReviews(res.data);
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

  const deleteAsync = async (reviewId: string) => {
    setLoading(true);
    try {
      await reviewApi.deleteReview(reviewId);
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
    setBookId,
    updateAsync,
    deleteAsync,
    createAsync,
  };
}
