import ApiBase from "./apibase";
import { ApiResponse } from "./apibase";
import {
  BookWithReviews,
  Review,
  BookInfo,
  ReviewUser,
} from "../../types/data";
import { toDate } from "../utils/date";

type BooksWithResponse = {
  books_with_reviews: BookWithReviews[];
};

export default class BookWithReviewsApi extends ApiBase {
  async getLatest(
    maxCount: number = 100
  ): Promise<ApiResponse<BooksWithResponse>> {
    const result = await this.getAsync<ApiRawResp>(
      `/book_with_reviews/latest/${maxCount}`
    );
    return { data: convert(result.data) };
  }
}

const convert = (data: ApiRawResp): BooksWithResponse => {
  const converted = data.books_with_reviews.map((x) => adjust(x));
  return { books_with_reviews: converted };
};

const adjust = (data: ApiBookWithReviews): BookWithReviews => {
  const adjusted: BookWithReviews = { ...data };
  adjusted.bookId = data.book_id;
  adjusted.publishedAt = toDate(data.published_at);
  adjusted.reviews = data.reviews.map((x) => {
    const rev: Review = { ...x };
    rev.reviewId = x.review_id;
    rev.isDraft = x.is_draft;
    rev.completedAt = x.completed_at ? toDate(x.completed_at) : null;
    rev.lastModifiedAt = toDate(x.last_modified_at);

    const user: ReviewUser = { ...x.user };
    user.userId = (x.user as ApiReviewUser).user_id;
    rev.user = user;
    return rev;
  });

  return adjusted;
};

type ApiBookInfo = BookInfo & {
  book_id: string;
  published_at: string;
};

type ApiReview = Review & {
  review_id: string;
  is_draft: boolean;
  completed_at: string;
  last_modified_at: string;
};

export type ApiReviewUser = ReviewUser & {
  user_id: string;
};

type ApiBookWithReviews = ApiBookInfo & {
  reviews: ApiReview[];
};

type ApiRawResp = {
  books_with_reviews: ApiBookWithReviews[];
};
