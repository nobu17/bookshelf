import { useState } from "react";
import BooksApi, { BookCreateParameter } from "../libs/apis/books";
import ReviewsApi from "../libs/apis/reviews";
import useAuthApi from "./UseAuthApi";
import { ReviewEditInfo } from "../components/parts/BookReviewEditForm";
import { creteNewBookAndReview } from "../libs/services/reviewCreateWorkflow";
import { BookWithMyReviewsApi } from "../libs/apis/bookWithReviews";
import { ValidationError } from "../types/errors";
import { toError } from "../libs/utils/error";

const booksApi = new BooksApi();
const reviewsApi = new ReviewsApi();
const bookReviewApi = new BookWithMyReviewsApi();

export default function useBookAndReviewCreate() {
  useAuthApi(booksApi);
  useAuthApi(reviewsApi);
  useAuthApi(bookReviewApi);
  const [error, setError] = useState<Error>();
  const [loading, setLoading] = useState(false);

  const createAsync = async (
    createBook: BookCreateParameter,
    createReview: ReviewEditInfo
  ) : Promise<ValidationError | null> => {
    setError(undefined);
    setLoading(true);
    try {
      await creteNewBookAndReview(
        booksApi,
        reviewsApi,
        bookReviewApi,
        createBook,
        createReview
      );
      return null;
    } catch (e: unknown) {
      console.error(e);
      if (e instanceof ValidationError) {
        setError(undefined);
        return e;
      }
      setError(toError(e));
      return null;
    } finally {
      setLoading(false);
    }
  };

  return {
    createAsync,
    loading,
    error,
  };
}
