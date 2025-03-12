import {
  Review,
  ReviewState,
  ReviewStateDef,
  toJapanese,
  copyReview,
} from "../../types/data";

import styles from "./BookCardRibbon.module.css";

type BookCardRibbonProps = {
  reviews: Review[];
};

export default function BookCardRibbon(props: BookCardRibbonProps) {
  return renderRibbon(props.reviews);
}

function renderRibbon(reviews: Review[]) {
  if (reviews.length === 0) {
    return <></>;
  }
  if (reviews.length === 1) {
    return renderStandardRibbon(reviews[0].state);
  }
  return renderAggregateRibbon(reviews);
}

const renderStandardRibbon = (state: ReviewState) => {
  const label = toJapanese(state);
  switch (state) {
    case ReviewStateDef.NotYet:
      return <span className={`${styles.ribbon} ${styles.grey}`}>{label}</span>;
    case ReviewStateDef.InProgress:
      return <span className={`${styles.ribbon} ${styles.blue}`}>{label}</span>;
    case ReviewStateDef.Completed:
      return <span className={`${styles.ribbon} ${styles.red}`}>{label}</span>;
    default:
      return <></>;
  }
};

const renderAggregateRibbon = (reviews: Review[]) => {
  const copied = reviews.map((x) => copyReview(x));
  const orderByLatest = copied.sort(
    (a, b) => a.lastModifiedAt.getTime() - b.lastModifiedAt.getTime()
  );
  const latest = orderByLatest[0];
  if (latest.state === ReviewStateDef.Completed) {
    const label = toJapanese(latest.state);
    return <span className={`${styles.ribbon} ${styles.red}`}>{label}</span>;
  }
  const prev = orderByLatest[1];
  if (
    latest.state === ReviewStateDef.InProgress &&
    prev.state === ReviewStateDef.Completed
  ) {
    return <span className={`${styles.ribbon} ${styles.red}`}>再読中</span>;
  }
};
