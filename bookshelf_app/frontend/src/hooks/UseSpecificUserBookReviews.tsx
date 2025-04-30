import { useEffect, useState } from "react";
import BookWithReviewsApi from "../libs/apis/bookWithReviews";
import { BookWithReviews, ReviewState, ReviewStateDef } from "../types/data";
import { ApiError } from "../libs/apis/apibase";
import { DisplayOption } from "../types/dsiplay";

const api = new BookWithReviewsApi();
const initialOption: DisplayOption = {
  isDisplayComplete: true,
  isDisplayInProgress: true,
  isDisplayNotYet: true,
};

export default function useSpecificUserBookReviews(initialUserId: string) {
  const [userId, setUserId] = useState<string>(initialUserId);
  const [userName, setUserName] = useState<string>("");
  const [bookWithReviews, setBookWithReviews] = useState<BookWithReviews[]>([]);
  const [filteredReviews, setFilteredReviews] = useState<BookWithReviews[]>([]);
  const [displayOption, setDisplayOption] =
    useState<DisplayOption>(initialOption);
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

  useEffect(() => {
    const filtered = filterByOptions(bookWithReviews, displayOption);
    setFilteredReviews(filtered);
  }, [displayOption, bookWithReviews]);

  const loadAsync = async (userId: string) => {
    setLoading(true);
    try {
      const res = await api.getSpecificUserReviews(userId);
      setBookWithReviews(res.data.books_with_reviews);
      setUserName(res.data.user_name);
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
    filteredReviews,
    displayOption,
    setDisplayOption,
    userName,
    error,
    loading,
    setUserId,
  };
}

const filterByOptions = (
  originals: BookWithReviews[],
  option: DisplayOption
): BookWithReviews[] => {
  const filtered: BookWithReviews[] = [];
  if (option.isDisplayComplete) {
    filtered.push(
      ...filterByState(originals, ReviewStateDef.Completed, filtered)
    );
  }
  if (option.isDisplayInProgress) {
    filtered.push(
      ...filterByState(originals, ReviewStateDef.InProgress, filtered)
    );
  }
  if (option.isDisplayNotYet) {
    filtered.push(...filterByState(originals, ReviewStateDef.NotYet, filtered));
  }
  return filtered;
};

const filterByState = (
  originals: BookWithReviews[],
  condition: ReviewState,
  currentItems: BookWithReviews[]
): BookWithReviews[] => {
  const targets = originals.filter((x) =>
    x.reviews.some((review) => review.state === condition)
  );
  const existingIds = new Set(currentItems.map((r) => r.bookId));
  return targets.filter((r) => !existingIds.has(r.bookId));
};
