import CardMedia from "@mui/material/CardMedia";
import Typography from "@mui/material/Typography";
import Box from "@mui/material/Box";
import Stack from "@mui/material/Stack";

import styles from "./BookCard.module.css";
import {
  BookWithReviews,
  ReviewState,
  ReviewStateDef,
  toJapanese,
} from "../../types/data";
import { getImageUrl } from "../../libs/utils/image";

type BookCardProps = {
  book: BookWithReviews;
  isRibbonRender?: boolean;
  onSelect: (bookId: string) => void;
};

export default function BookCard(props: BookCardProps) {
  const { bookId, title, isbn13 } = props.book;
  const { book, isRibbonRender } = props;
  const { onSelect } = props;
  return (
    <>
      <Stack
        className={styles.box}
        direction="column"
        spacing={0}
        sx={{
          justifyContent: "center",
          alignItems: "center",
        }}
        onClick={() => onSelect(bookId)}
      >
        {isRibbonRender ? renderRibbon(book) : <></>}
        <CardMedia
          component="img"
          height="200"
          sx={{ padding: "1em 0em 0em 0em", objectFit: "contain" }}
          image={getImageUrl(isbn13)}
        />
        <Box
          sx={{
            display: "flex",
            justifyContent: "space-between",
          }}
        >
          <Typography
            sx={{
              mb: 2,
              fontWeight: "bold",
              wordBreak: "break-word",
              maxWidth: 200,
            }}
          >
            {title}
          </Typography>
        </Box>
      </Stack>
    </>
  );
}

function renderRibbon(book: BookWithReviews) {
  const { reviews } = book;
  if (reviews.length === 0) {
    return <></>;
  }
  if (reviews.length === 1) {
    return renderStandardRibbon(reviews[0].state);
  }
  return renderAggregateRibbon(book);
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

const renderAggregateRibbon = (book: BookWithReviews) => {
  const order_by_latest = [...book.reviews].sort(
    (a, b) => a.lastModifiedAt.getTime() - b.lastModifiedAt.getTime()
  );
  const latest = order_by_latest[0];
  if (latest.state === ReviewStateDef.Completed) {
    const label = toJapanese(latest.state);
    return <span className={`${styles.ribbon} ${styles.red}`}>{label}</span>;
  }
};
