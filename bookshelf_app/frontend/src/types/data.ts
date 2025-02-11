export type BookInfo = {
  bookId: string;
  isbn13: string;
  title: string;
  publisher: string;
  authors: string[];
  published_at: Date;
  tags: BookTag[];
};

export type BookTag = {
  id: string;
  name: string;
};

export type Review = {
  reviewId: string;
  content: string;
  isDraft: boolean;
  state: ReviewState;
  completedAt: Date;
  lastModifiedAt: Date;
};

const ReviewStateDef = {
  NotYet: 0,
  InProgress: 1,
  Completed: 2,
} as const;

type ReviewState = (typeof ReviewStateDef)[keyof typeof ReviewStateDef];

export function toJapanese(state: ReviewState) {
  switch (state) {
    case ReviewStateDef.NotYet:
      return "未読";
    case ReviewStateDef.InProgress:
      return "読書中";
    case ReviewStateDef.Completed:
      return "完了";
  }
}

export type BookWithReviews = BookInfo & {
  reviews: Review[]
}

