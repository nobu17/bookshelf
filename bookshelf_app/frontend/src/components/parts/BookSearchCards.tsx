import Grid from "@mui/material/Grid2";

import BookSearchCard from "./BookSearchCard";
import { NdlBookWithReviews } from "../../types/ndls";

type BookSearchCardsProps = {
  books: NdlBookWithReviews[];
  onSelect: (book: NdlBookWithReviews) => void;
};

export default function BookSearchCards(props: BookSearchCardsProps) {
  const { books, onSelect } = props;

  const handleSelect = ({
    title,
    isbn13,
  }: {
    title: string;
    isbn13: string;
  }) => {
    const found = books.find((x) => x.isbn13 === isbn13 && x.title === title);
    if (found) {
      onSelect(found);
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
          <Grid size={{ xs: 6, md: 3 }} sx={{ border: 2 }} key={(book.isbn13 + book.title)}>
            <BookSearchCard
              book={book}
              onSelect={handleSelect}
            ></BookSearchCard>
          </Grid>
        ))}
      </Grid>
    </>
  );
}
