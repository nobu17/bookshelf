import ApiBase, { ApiError } from "./apibase";
import { ApiResponse } from "./apibase";
import {
  BookWithReviews,
  Review,
  ReviewState,
  ReviewUser,
} from "../../types/data";
import { toDate } from "../utils/date";
import { ApiBookTag, convertToBookTags } from "./bookTags";

type BooksWithResponse = {
  books_with_reviews: BookWithReviews[];
};

type SpecificUserBooksWithResponse = {
  books_with_reviews: BookWithReviews[];
  user_name: string;
};

type BookWithResponse = BookWithReviews;

export default class BookWithReviewsApi extends ApiBase {
  async getLatest(
    maxCount: number = 100
  ): Promise<ApiResponse<BooksWithResponse>> {
    const result = await this.getAsync<ApiRawResp>(
      `/book_with_reviews/latest/${maxCount}`
    );
    return { data: convert(result.data) };
  }
  async getSpecificUserReviews(
    userId: string
  ): Promise<ApiResponse<SpecificUserBooksWithResponse>> {
    const result = await this.getAsync<ApiSpecificUserRawResp>(
      `/book_with_reviews/user_id/${userId}`
    );
    return { data: convert_specific_user(result.data) };
  }
}

export class BookWithMyReviewsApi extends ApiBase {
  async getMyReviews(): Promise<ApiResponse<BooksWithResponse>> {
    const result = await this.getAsync<ApiRawResp>(`/book_with_reviews/me`);
    return { data: convert(result.data) };
  }
  async getMyReviewsForEdit(): Promise<ApiResponse<BooksWithResponse>> {
    const result = await this.getAsync<ApiRawResp>(
      `/book_with_reviews/for_edit/me`
    );
    return { data: convert(result.data) };
  }
  async getMyReviewForEditByBookId(
    bookId: string
  ): Promise<ApiResponse<BookWithResponse>> {
    const result = await this.getAsync<ApiBookWithReviews>(
      `/book_with_reviews/for_edit/book_id/${bookId}`
    );
    return { data: adjust(result.data) };
  }
}

const convert = (data: ApiRawResp): BooksWithResponse => {
  assertBooksWithReviewsResponse(data);
  const converted = data.books_with_reviews.map((x) => adjust(x));
  return { books_with_reviews: converted };
};

const convert_specific_user = (
  data: ApiSpecificUserRawResp
): SpecificUserBooksWithResponse => {
  assertBooksWithReviewsResponse(data);
  const converted = data.books_with_reviews.map((x) => adjust(x));
  return { books_with_reviews: converted, user_name: data.user_name };
};

const adjust = (data: ApiBookWithReviews): BookWithReviews => {
  return {
    bookId: data.book_id,
    isbn13: data.isbn13,
    title: data.title,
    publisher: data.publisher,
    authors: data.authors,
    publishedAt: toDate(data.published_at),
    imageUrl: data.image_url || null,
    tags: convertToBookTags(data.tags),
    reviews: (data.reviews ?? []).map((review) => convertToReview(review)),
  };
};

const assertBooksWithReviewsResponse = (
  data: ApiRawResp | ApiSpecificUserRawResp
): void => {
  if (!Array.isArray(data?.books_with_reviews)) {
    throw new ApiError(
      new Error("books_with_reviews is missing from API response."),
      0,
      "books_with_reviews is missing from API response."
    );
  }
};

const convertToReview = (review: ApiReview): Review => {
  return {
    reviewId: review.review_id,
    content: review.content,
    isDraft: review.is_draft,
    state: review.state,
    completedAt: review.completed_at ? toDate(review.completed_at) : null,
    lastModifiedAt: toDate(review.last_modified_at),
    user: convertToReviewUser(review.user),
  };
};

const convertToReviewUser = (user: ApiReviewUser): ReviewUser => {
  return {
    userId: user.user_id,
    name: user.name,
  };
};

type ApiBookInfo = {
  book_id: string;
  isbn13: string;
  title: string;
  publisher: string;
  authors: string[];
  published_at: string;
  image_url: string | null;
  tags: ApiBookTag[];
};

type ApiReview = {
  review_id: string;
  content: string;
  is_draft: boolean;
  state: ReviewState;
  completed_at: string | null;
  last_modified_at: string;
  user: ApiReviewUser;
};

export type ApiReviewUser = {
  user_id: string;
  name: string;
};

type ApiBookWithReviews = ApiBookInfo & {
  reviews: ApiReview[];
};

type ApiRawResp = {
  books_with_reviews: ApiBookWithReviews[];
};

type ApiSpecificUserRawResp = {
  books_with_reviews: ApiBookWithReviews[];
  user_name: string;
};
