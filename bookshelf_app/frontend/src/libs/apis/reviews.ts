import ApiBase, { ApiResponse } from "./apibase";
import { ReviewState } from "../../types/data";
import { toISOStringWithTimezone } from "../utils/date";

export default class ReviewsApi extends ApiBase {
  async updateReview(
    reviewId: string,
    updateReview: UpdateReviewParameter
  ): Promise<void> {
    return await this.putAsync(
      `/reviews/${reviewId}`,
      convertToApiReviewParameter(updateReview)
    );
  }
  async createReview(
    createReview: CreateReviewParameter
  ): Promise<ApiResponse<CreateReviewResponse>> {
    const resp = await this.postAsync<ApiCreateReviewResponse>(
      `/reviews`,
      convertToApiCreateReviewParameter(createReview)
    );
    return { data: { reviewId: resp.data.review_id } };
  }
}

export type UpdateReviewParameter = {
  content: string;
  state: ReviewState;
  isDraft: boolean;
  completedAt: Date | null;
};

type ApiReviewParameter = {
  content: string;
  state: ReviewState;
  is_draft: boolean;
  completed_at: string | null;
};

const convertToApiReviewParameter = (
  base: UpdateReviewParameter
): ApiReviewParameter => {
  return {
    content: base.content,
    state: base.state,
    is_draft: base.isDraft,
    completed_at: base.completedAt
      ? toISOStringWithTimezone(base.completedAt)
      : null,
  };
};

export type CreateReviewParameter = {
  bookId: string;
  content: string;
  state: ReviewState;
  isDraft: boolean;
  completedAt: Date | null;
};

const convertToApiCreateReviewParameter = (
  base: CreateReviewParameter
): ApiCreateReviewParameter => {
  return {
    book_id: base.bookId,
    content: base.content,
    state: base.state,
    is_draft: base.isDraft,
    completed_at: base.completedAt
      ? toISOStringWithTimezone(base.completedAt)
      : null,
  };
};

type ApiCreateReviewParameter = {
  book_id: string;
  content: string;
  state: ReviewState;
  is_draft: boolean;
  completed_at: string | null;
};

type ApiCreateReviewResponse = {
  review_id: string;
};

export type CreateReviewResponse = {
  reviewId: string;
};
