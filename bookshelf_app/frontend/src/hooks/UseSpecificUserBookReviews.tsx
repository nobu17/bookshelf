import { useEffect, useState } from "react";
import BookWithReviewsApi from "../libs/apis/bookWithReviews";
import {
  BookWithReviews,
  ReviewState,
  ReviewStateDef,
  getLatestCompletedAt,
  getOldestCompletedAt,
  getLatestLastModifiedAt,
  getOldestLastModifiedAt,
} from "../types/data";
import { ApiError } from "../libs/apis/apibase";
import {
  DisplayOption,
  DisplayOrderOptionDef,
  DisplayOrderOption,
} from "../types/display";

const api = new BookWithReviewsApi();
const initialOption: DisplayOption = {
  isDisplayComplete: true,
  isDisplayInProgress: true,
  isDisplayNotYet: true,
  order: DisplayOrderOptionDef.CompletedDesc,
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
    const sorted = sortByDate(filtered, displayOption.order);
    setFilteredReviews(sorted);
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
    loadAsync,
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

const sortByDate = (
  items: BookWithReviews[],
  option: DisplayOrderOption
): BookWithReviews[] => {
  const sortFunc = sortBookStrategyMap[option];
  return sortFunc(items);
};

const sortBooksByLatestCompletedAt = (
  books: BookWithReviews[]
): BookWithReviews[] => {
  return sortByLatestBooks(books, getLatestCompletedAt);
};

const sortBooksByOldestCompletedAt = (
  books: BookWithReviews[]
): BookWithReviews[] => {
  return sortByOldestBooks(books, getOldestCompletedAt);
};

const sortBooksByLatestLastModifiedAt = (
  books: BookWithReviews[]
): BookWithReviews[] => {
  return sortByLatestBooks(books, getLatestLastModifiedAt);
};

const sortBooksByOldestLastModifiedAt = (
  books: BookWithReviews[]
): BookWithReviews[] => {
  return sortByOldestBooks(books, getOldestLastModifiedAt);
};

const sortBookStrategyMap: Record<
  DisplayOrderOption,
  (books: BookWithReviews[]) => BookWithReviews[]
> = {
  [DisplayOrderOptionDef.CompletedDesc]: sortBooksByLatestCompletedAt,
  [DisplayOrderOptionDef.CompletedAsc]: sortBooksByOldestCompletedAt,
  [DisplayOrderOptionDef.EditedDesc]: sortBooksByLatestLastModifiedAt,
  [DisplayOrderOptionDef.EditedAsc]: sortBooksByOldestLastModifiedAt,
};

const sortByLatestBooks = (
  books: BookWithReviews[],
  getDate: (book: BookWithReviews) => Date | null
): BookWithReviews[] => {
  return [...books].sort((a, b) => {
    const latestA = getDate(a);
    const latestB = getDate(b);

    // 両方 null
    if (latestA === null && latestB === null) return 0;
    // A が null → 後ろへ
    if (latestA === null) return 1;
    // B が null → 前へ
    if (latestB === null) return -1;
    // 降順（新しい日付が先）
    return latestB.getTime() - latestA.getTime();
  });
};

const sortByOldestBooks = (
  books: BookWithReviews[],
  getDate: (book: BookWithReviews) => Date | null
): BookWithReviews[] => {
  return [...books].sort((a, b) => {
    const latestA = getDate(a);
    const latestB = getDate(b);

    // 両方 null
    if (latestA === null && latestB === null) return 0;
    // A が null → 後ろへ
    if (latestA === null) return 1;
    // B が null → 前へ
    if (latestB === null) return -1;
    // 照順（古い日付が先）
    return latestA.getTime() - latestB.getTime();
  });
};

// type ReviewDatePair =
//   | { completed: Date; lastModified?: never }
//   | { completed: null; lastModified: Date };
