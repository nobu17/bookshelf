import { BookWithReviews, Review } from "./data";

export type FilteredReviews = {
  originals: BookWithReviews[];
  filtered: FilteredBookWithReviews[];
};

export type FilteredBookWithReviews = BookWithReviews & {
  filteredReviews: Review[];
  representative: Review | null;
};
export const FilterConditionDef = {
  All: 0,
  OnlyCompleted: 1,
  OnlyInProgress: 2,
  OnlyNotYet: 3,
} as const;

export type FilterCondition =
  (typeof FilterConditionDef)[keyof typeof FilterConditionDef];

export const AllFilterConditions: FilterCondition[] = [
  FilterConditionDef.All,
  FilterConditionDef.OnlyCompleted,
  FilterConditionDef.OnlyInProgress,
  FilterConditionDef.OnlyNotYet,
];

export function toJapanese(state: FilterCondition): string {
  switch (state) {
    case FilterConditionDef.All:
      return "全て";
    case FilterConditionDef.OnlyCompleted:
      return "読了";
    case FilterConditionDef.OnlyInProgress:
      return "読中";
    case FilterConditionDef.OnlyNotYet:
      return "未読";
  }
}
