import {
  Review,
  ReviewState,
  ReviewStateDef,
  toJapanese,
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
  const inProgs = reviews.filter((x) => x.state === ReviewStateDef.InProgress);
  const comps = reviews.filter((x) => x.state === ReviewStateDef.Completed);
  if (inProgs.length > 0) {
    const inProgMsg = toJapanese(inProgs[0].state);
    if (comps.length > 0) {
      return (
        <span className={`${styles.ribbon} ${styles.blue}`}>再{inProgMsg}</span>
      );
    } else {
      return (
        <span className={`${styles.ribbon} ${styles.blue}`}>{inProgMsg}</span>
      );
    }
  }
  const notYet = reviews.filter((x) => x.state === ReviewStateDef.NotYet);
  if (notYet.length > 0) {
    return (
      <span className={`${styles.ribbon} ${styles.grey}`}>
        {toJapanese(notYet[0].state)}
      </span>
    );
  }
  if (comps.length > 0) {
    return (
      <span className={`${styles.ribbon} ${styles.red}`}>
        {toJapanese(comps[0].state)}
      </span>
    );
  }
};
