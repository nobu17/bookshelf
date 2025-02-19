import Grid from "@mui/material/Grid2";

import BookCard from "./BookCard";
import { BookWithReviews } from "../../types/data";

type BookCardsProps = {
  books: BookWithReviews[];
  isRibbonRender?: boolean;
  onSelect: (book: BookWithReviews) => void;
};

export default function BookCards(props: BookCardsProps) {
  const { books, isRibbonRender, onSelect } = props;
  const handleSelect = (bookId: string) => {
    const book = books.find((x) => x.bookId == bookId);
    if (book) {
      onSelect(book);
    }
  };
  return (
    <>
      <Grid
        container
        spacing={1}
        sx={{
          alignItems: "stretch",
          mx: 1,
        }}
      >
        {books.map((book) => (
          <Grid size={{ xs: 6, md: 3 }} sx={{ border: 2 }} key={book.bookId}>
            <BookCard
              book={book}
              isRibbonRender={isRibbonRender}
              onSelect={handleSelect}
            ></BookCard>
          </Grid>
        ))}
      </Grid>
    </>
  );
}
