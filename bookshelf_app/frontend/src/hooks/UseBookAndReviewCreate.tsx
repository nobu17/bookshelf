import { useState } from "react";
import BooksApi, { BookCreateParameter } from "../libs/apis/books";
import ReviewsApi from "../libs/apis/reviews";
import useAuthApi from "./UseAuthApi";
import { ApiError } from "../libs/apis/apibase";
import { ReviewEditInfo } from "../components/parts/BookReviewEditForm";

const booksApi = new BooksApi();
const reviewsApi = new ReviewsApi();

export default function useBookAndReviewCreate() {
  useAuthApi(booksApi);
  useAuthApi(reviewsApi);
  const [error, setError] = useState<Error>();
  const [loading, setLoading] = useState(false);

  const create = async (
    createBook: BookCreateParameter,
    createReview: ReviewEditInfo
  ) => {
    setError(undefined);
    setLoading(true);
    try {
      // only when book info not exists, need to create
      let bookId = await fetchBookId(createBook.isbn13);
      if (!bookId) {
        const book = await booksApi.create(createBook);
        bookId = book.data.bookId;
      }
      // attach book Id to review
      const createReviewInfo = { ...createReview, bookId: bookId };
      await reviewsApi.createReview(createReviewInfo);
    } catch (e: unknown) {
      console.error(e);
      if (e instanceof Error) {
        setError(e);
        return;
      }
      setError(new Error("unexpected error."));
    } finally {
      setLoading(false);
    }
  };

  const fetchBookId = async (isbn13: string): Promise<string | null> => {
    try {
      // if can api call correctly, means that book is exists
      const res = await booksApi.findByIsbn13(isbn13);
      // currently api do not return 0 length, but check for unexpected data
      if (res.data.books.length === 0) {
        return null;
      }
      return res.data.books[0].isbn13;
    } catch (e: unknown) {
      // if not found, return 404
      if (e instanceof ApiError) {
        if (e.isNotFound()) {
          return null;
        }
      }
      throw e;
    }
  };

  return {
    create,
    loading,
    error,
  };
}
