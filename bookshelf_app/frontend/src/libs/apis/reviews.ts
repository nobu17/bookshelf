import ApiBase from "./apibase";
import { Review, ReviewState } from "../../types/data";
import { toISOStringWithTimezone } from "../utils/date";

export default class ReviewsApi extends ApiBase {
  async updateReview(reviewId: string, updateReview: Review): Promise<void> {
    return await this.putAsync(`/reviews/${reviewId}`, convert(updateReview));
  }
}

const convert = (data: Review): ApiReview => {
  const user: ApiReviewUser = { ...data.user, user_id: data.user.userId };
  const converted: ApiReview = {
    ...data,
    review_id: data.reviewId,
    is_draft: data.isDraft,
    completed_at: data.completedAt ? toISOStringWithTimezone(data.completedAt) : null,
    last_modified_at: toISOStringWithTimezone(data.lastModifiedAt),
    user: user,
  };
  return converted;
};

type ApiReview = {
  review_id: string;
  content: string;
  state: ReviewState;
  is_draft: boolean;
  completed_at: string | null;
  last_modified_at: string;
  user: ApiReviewUser;
};

type ApiReviewUser = {
  user_id: string;
  name: string;
};
