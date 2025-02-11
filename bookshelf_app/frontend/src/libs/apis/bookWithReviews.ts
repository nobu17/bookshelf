import ApiBase from "./apibase";
import { ApiResponse } from "./apibase";
import { BookWithReviews } from "../../types/data";

type BooksWithResponse = {
  books_with_reviews: BookWithReviews[];
};

export default class BookWithReviewsApi extends ApiBase {
  async getLatest(maxCount: number = 100): Promise<ApiResponse<BooksWithResponse>> {
    const result = await this.getAsync<BooksWithResponse>(`/books/reviews/latest/${maxCount}`);
    return result;
  }
}
