export type BookInfo = {
  bookId: string;
  isbn13: string;
  title: string;
  publisher: string;
  authors: string[];
  publishedAt: Date;
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
  completedAt: Date | null;
  lastModifiedAt: Date;
  user: ReviewUser;
};

export const ReviewStateDef = {
  NotYet: 0,
  InProgress: 1,
  Completed: 2,
} as const;

export type ReviewState = (typeof ReviewStateDef)[keyof typeof ReviewStateDef];

export function toJapanese(state: ReviewState) {
  switch (state) {
    case ReviewStateDef.NotYet:
      return "未読";
    case ReviewStateDef.InProgress:
      return "読中";
    case ReviewStateDef.Completed:
      return "読了";
  }
}

export type ReviewUser = {
  userId: string;
  name: string;
};

export type BookWithReviews = BookInfo & {
  reviews: Review[];
};

export type UserToken = {
  token: string;
  user: AuthUserInfo;
};

export type AuthUserInfo = {
  userId: string;
  name: string;
  roles: string[];
};
