import { useEffect, useState } from "react";
import {
  BookWithReviews,
  copyBookWithReviews,
  Review,
  ReviewStateDef,
} from "../types/data";
import {
  FilterCondition,
  FilterConditionDef,
  FilteredBookWithReviews,
  FilteredReviews,
} from "../types/filter";

export default function useFilterReviews(reviews: BookWithReviews[]) {
  useState<BookWithReviews[]>(reviews);
  const [filtered, setFiltered] = useState<FilteredReviews>();
  const [condition, setCondition] = useState<FilterCondition>(
    FilterConditionDef.All
  );

  useEffect(() => {
    const fil = filteredByCondition(reviews, condition);
    setFiltered(fil);
  }, [condition, reviews]);

  return {
    condition,
    setCondition,
    filtered,
  };
}

const filteredByCondition = (
  reviews: BookWithReviews[],
  condition: FilterCondition
): FilteredReviews => {
  const copied = reviews.map((x) => copyBookWithReviews(x));
  const filtered: FilteredBookWithReviews[] = [];
  if (condition === FilterConditionDef.All) {
    for (const book of copied) {
      const notComp = book.reviews.find(
        (x) => x.state !== ReviewStateDef.Completed
      );
      const allComps = book.reviews.filter(
        (x) => x.state === ReviewStateDef.Completed
      );
      allComps.sort((a, b) => sortCompletedAt(a, b));
      const latestComp = allComps.length > 0 ? allComps[0] : null;

      let representative: Review | null = null;
      if (notComp) {
        representative = notComp;
      } else if (latestComp) {
        representative = latestComp;
      }

      filtered.push({
        ...book,
        filteredReviews: book.reviews,
        representative: representative,
      });
    }
    return {
      originals: reviews,
      filtered: filtered,
    };
  }
  if (condition === FilterConditionDef.OnlyCompleted) {
    for (const book of copied) {
      const allComps = book.reviews.filter(
        (x) => x.state === ReviewStateDef.Completed
      );
      if (allComps.length === 0) {
        continue;
      }
      allComps.sort((a, b) => sortCompletedAt(a, b));
      const latestComp = allComps.length > 0 ? allComps[0] : null;
      filtered.push({
        ...book,
        filteredReviews: allComps,
        representative: latestComp,
      });
    }
    return {
      originals: reviews,
      filtered: filtered,
    };
  }
  // other condition is ensured only 1
  for (const book of copied) {
    const alls = book.reviews.filter((x) => x.state === condition);
    if (alls.length === 0) {
      continue;
    }
    const representative = alls.find((x) => x.state === condition);

    filtered.push({
      ...book,
      filteredReviews: alls,
      representative: representative ?? null,
    });
  }
  return {
    originals: reviews,
    filtered: filtered,
  };
};

const sortCompletedAt = (a: Review, b: Review) => {
  const aFromDate = a.completedAt ?? new Date(0);
  const bFromDate = b.completedAt ?? new Date(0);
  return aFromDate < bFromDate ? 1 : -1;
};
