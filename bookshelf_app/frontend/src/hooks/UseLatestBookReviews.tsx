import { useEffect, useState } from "react";
import BookWithReviewsApi from "../libs/apis/bookWithReviews";
import { BookWithReviews } from "../types/data";
import { ApiError } from "../libs/apis/apibase";
import { toError } from "../libs/utils/error";

const api = new BookWithReviewsApi();

export default function useLatestBookReviews() {
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
      const res = await api.getLatest();
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
      setError(toError(e));
    } finally {
      setLoading(false);
    }
  };

  return {
    bookWithReviews,
    error,
    loading,
    loadAsync,
  };
}
