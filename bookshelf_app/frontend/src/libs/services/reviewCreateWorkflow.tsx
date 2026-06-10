import { ReviewEditInfo } from "../../components/parts/BookReviewEditForm";
import { BookInfo, Review, ReviewStateDef, toJapanese } from "../../types/data";
import { ValidationError } from "../../types/errors";
import { ApiError } from "../apis/apibase";
import BooksApi, { BookCreateParameter } from "../apis/books";
import { BookWithMyReviewsApi } from "../apis/bookWithReviews";
import ReviewsApi from "../apis/reviews";
import TagsApi from "../apis/tags";
import { mergeBookTagsByNames } from "./bookTags";

export const creteNewBookAndReview = async (
  bookApi: BooksApi,
  reviewApi: ReviewsApi,
  bookReviewApi: BookWithMyReviewsApi,
  tagsApi: TagsApi,
  createBook: BookCreateParameter,
  createReview: ReviewEditInfo,
  tagNames: string[] = []
) => {
  // only when book info not exists, need to create
  let book = await fetchBook(bookApi, createBook.isbn13);
  if (!book) {
    book = (await bookApi.create(createBook)).data;
  }
  const validateError = await validateNewReview(
    bookReviewApi,
    book.bookId,
    createReview
  );
  if (validateError !== null) {
    throw validateError;
  }
  await mergeBookTagsByNames(
    bookApi,
    tagsApi,
    book.bookId,
    book.tags,
    tagNames
  );
  // attach book Id to review
  const createReviewInfo = { ...createReview, bookId: book.bookId };
  await reviewApi.createReview(createReviewInfo);
};

export const createNewReview = async (
  bookReviewApi: BookWithMyReviewsApi,
  reviewApi: ReviewsApi,
  bookId: string,
  createReview: ReviewEditInfo
) => {
  const validateError = await validateNewReview(
    bookReviewApi,
    bookId,
    createReview
  );
  if (validateError !== null) {
    throw validateError;
  }
  // attach book Id to review
  const createReviewInfo = { ...createReview, bookId: bookId };
  await reviewApi.createReview(createReviewInfo);
};

export const updateReview = async (
  bookReviewApi: BookWithMyReviewsApi,
  reviewApi: ReviewsApi,
  bookId: string,
  reviewId: string,
  updateReview: Review
) => {
  const validateError = await validateUpdateReview(
    bookReviewApi,
    bookId,
    updateReview
  );
  if (validateError !== null) {
    throw validateError;
  }
  await reviewApi.updateReview(reviewId, updateReview);
};

const fetchBook = async (
  bookApi: BooksApi,
  isbn13: string
): Promise<BookInfo | null> => {
  try {
    // if can api call correctly, means that book is exists
    const res = await bookApi.findByIsbn13(isbn13);
    // currently api do not return 0 length, but check for unexpected data
    if (res.data.books.length === 0) {
      return null;
    }
    return res.data.books[0];
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

const validateNewReview = async (
  bookReviewApi: BookWithMyReviewsApi,
  bookId: string,
  target: ReviewEditInfo
): Promise<ValidationError | null> => {
  const reviews = await bookReviewApi.getMyReviewForEditByBookId(bookId);
  return validateCreateState(target, reviews.data.reviews);
};

const validateUpdateReview = async (
  bookReviewApi: BookWithMyReviewsApi,
  bookId: string,
  target: Review
): Promise<ValidationError | null> => {
  const reviews = await bookReviewApi.getMyReviewForEditByBookId(bookId);
  // filter self
  return validateCreateState(
    target,
    reviews.data.reviews.filter((x) => x.reviewId !== target.reviewId)
  );
};

const validateCreateState = (
  target: ReviewEditInfo,
  existReviews: Review[]
): ValidationError | null => {
  // comp state is always allowed.
  if (target.state === ReviewStateDef.Completed) {
    return null;
  }
  const notCompReviews = existReviews.filter(
    (x) => x.state !== ReviewStateDef.Completed
  );
  if (notCompReviews.length > 0) {
    const allStates = notCompReviews.map((x) => toJapanese(x.state)).join(",");
    return new ValidationError(
      `[${toJapanese(
        ReviewStateDef.Completed
      )}]以外の状態は、同時に1つしか設定できません。 既存状態:${allStates} `
    );
  }
  return null;
};
