import { useEffect, useState } from "react";
import BookWithReviewsApi from "../libs/apis/bookWithReviews";
import { BookWithReviews } from "../types/data";
import { ApiError } from "../libs/apis/apibase";

const api = new BookWithReviewsApi();

export default function useSpecificUserBookReviews(initialUserId: string) {
  const [userId, setUserId] = useState<string>(initialUserId);
  const [bookWithReviews, setBookWithReviews] = useState<BookWithReviews[]>([]);
  const [error, setError] = useState<Error>();
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const init = async () => {
      await loadAsync(userId);
    };
    if (userId) {
      init();
    }
  }, [userId]);

  const loadAsync = async (userId: string) => {
    setLoading(true);
    try {
      const res = await api.getSpecificUserReviews(userId);
      setBookWithReviews(res.data.books_with_reviews);
    } catch (e: unknown) {
      if (e instanceof ApiError) {
        if (e.isBadRequest()) {
          setError(new Error("Invalid parameter"));
          return;
        }
        setError(e);
        return;
      } else if (e instanceof Error) {
        setError(e);
        return;
      }
      setError(new Error("Unexpected error."));
    } finally {
      setLoading(false);
    }
  };

  return {
    bookWithReviews,
    error,
    loading,
    setUserId,
  };
}
