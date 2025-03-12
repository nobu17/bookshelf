import CardMedia from "@mui/material/CardMedia";
import Typography from "@mui/material/Typography";
import Box from "@mui/material/Box";
import Stack from "@mui/material/Stack";

import { getImageUrl } from "../../libs/utils/image";
import { NdlBookWithReviews } from "../../types/ndls";
import BookCardRibbon from "./BookCardRibbon";
import styles from "./BookSearchCard.module.css";

type BookSearchCardProps = {
  book: NdlBookWithReviews;
  onSelect: (book: NdlBookWithReviews) => void;
};

export default function BookSearchCard(props: BookSearchCardProps) {
  const { title, isbn13 } = props.book;
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
