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

export function toJapanese(state: ReviewState): string {
  switch (state) {
    case ReviewStateDef.NotYet:
      return "未読";
    case ReviewStateDef.InProgress:
      return "読中";
    case ReviewStateDef.Completed:
      return "読了";
  }
}

export const AllReviewStates: ReviewState[] = [
  ReviewStateDef.NotYet,
  ReviewStateDef.InProgress,
  ReviewStateDef.Completed,
];

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

export const copyReview = (review: Review): Review => {
  const copied = JSON.parse(JSON.stringify(review), (key, value) => {
    if (value === null) {
      return null;
    }
    if (key === "lastModifiedAt" || key === "completedAt") {
      // parseは数値表現にするだけなのでDateコンストラクタに渡す
      return new Date(Date.parse(value));
    }
    return value;
  });
  return copied;
};

export const copyBookWithReviews = (book: BookWithReviews): BookWithReviews => {
  const copied = JSON.parse(JSON.stringify(book), (key, value) => {
    if (value === null) {
      return null;
    }
    if (key === "reviews") {
      return null;
    }
    return value;
  });
  copied.reviews = book.reviews.map((x) => copyReview(x));

  return copied;
};
