import CardMedia from "@mui/material/CardMedia";
import Typography from "@mui/material/Typography";
import Box from "@mui/material/Box";
import Stack from "@mui/material/Stack";

import styles from "./BookCard.module.css";
import { BookWithReviews } from "../../types/data";
import { getFallbackImageUrl, getImageUrl } from "../../libs/utils/image";
import BookCardRibbon from "./BookCardRibbon";

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
        {isRibbonRender ? <BookCardRibbon reviews={book.reviews} /> : <></>}
        <CardMedia
          component="img"
          height="200"
          sx={{ padding: "1em 0em 0em 0em", objectFit: "contain" }}
          image={getImageUrl(isbn13)}
          onError={(e) => {
            e.currentTarget.src = getFallbackImageUrl();
          }}
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
