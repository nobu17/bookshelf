import CardMedia from "@mui/material/CardMedia";
import Typography from "@mui/material/Typography";
import Box from "@mui/material/Box";
import Stack from "@mui/material/Stack";

import { getFallbackImageUrl, getSearchResultImageUrl } from "../../libs/utils/image";
import { BookSearchResultWithReviews } from "../../types/bookSearch";
import BookCardRibbon from "./BookCardRibbon";
import GoogleBooksAttribution from "./GoogleBooksAttribution";
import styles from "./BookSearchCard.module.css";

type BookSearchCardProps = {
  book: BookSearchResultWithReviews;
  onSelect: (book: BookSearchResultWithReviews) => void;
};

export default function BookSearchCard(props: BookSearchCardProps) {
  const { title } = props.book;
  const { book } = props;
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
        onClick={() => onSelect(book)}
      >
        <BookCardRibbon reviews={book.reviews} />
        <CardMedia
          component="img"
          height="200"
          sx={{ padding: "1em 0em 0em 0em", objectFit: "contain" }}
          image={getSearchResultImageUrl(book)}
          onError={(e) => {
            e.currentTarget.src = getFallbackImageUrl();
          }}
        />
        <GoogleBooksAttribution imageUrl={book.imageUrl} compact />
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
