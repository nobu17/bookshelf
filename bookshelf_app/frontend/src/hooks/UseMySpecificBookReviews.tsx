import { useEffect, useState } from "react";
import { BookWithMyReviewsApi } from "../libs/apis/bookWithReviews";
import { BookWithReviews, Review } from "../types/data";
import { ApiError } from "../libs/apis/apibase";
import useAuthApi from "./UseAuthApi";
import ReviewsApi from "../libs/apis/reviews";
import { ReviewEditInfo } from "../components/parts/BookReviewEditForm";
import {
  createNewReview,
  updateReview,
} from "../libs/services/reviewCreateWorkflow";
import { ValidationError } from "../types/errors";

const api = new BookWithMyReviewsApi();
const reviewApi = new ReviewsApi();

export default function useMySpecificBookReviews() {
  useAuthApi(api);
  useAuthApi(reviewApi);
  const [bookWithReviews, setBookWithReviews] =
    useState<BookWithReviews | null>(null);
  const [bookId, setBookId] = useState("");
  const [error, setError] = useState<Error>();

  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const init = async () => {
      await loadAsync();
    };
    if (bookId) {
      init();
    }
  }, [bookId]);

  const createAsync = async (
    bookId: string,
    createReview: ReviewEditInfo
  ): Promise<ValidationError | null> => {
    setLoading(true);
    try {
      await createNewReview(api, reviewApi, bookId, createReview);
      // reload
      const res = await api.getMyReviewForEditByBookId(bookId);
      setBookWithReviews(res.data);
      setError(undefined);
      return null;
    } catch (e: unknown) {
      if (e instanceof ApiError) {
        if (!e.isBadRequest()) {
          setError(e);
          return null;
        }
      } else if (e instanceof ValidationError) {
        setError(undefined);
        return e;
      } else if (e instanceof Error) {
        setError(e);
        return null;
      }
      setError(new Error("unexpected error."));
      return null;
    } finally {
      setLoading(false);
    }
  };

  const updateAsync = async (
    bookId: string,
    reviewId: string,
    review: Review
  ): Promise<ValidationError | null> => {
    setLoading(true);
    try {
      await updateReview(api, reviewApi, bookId, reviewId, review);
    } catch (e: unknown) {
      if (e instanceof ApiError) {
        if (!e.isBadRequest()) {
          setError(e);
          return null;
        }
      } else if (e instanceof ValidationError) {
        setError(undefined);
        return e;
      } else if (e instanceof Error) {
        setError(e);
        return null;
      }
      setError(new Error("unexpected error."));
      return null;
    } finally {
      setLoading(false);
    }
    await loadAsync();
    return null;
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
