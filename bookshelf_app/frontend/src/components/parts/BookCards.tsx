import Grid from "@mui/material/Grid2";

import BookCard from "./BookCard";
import { BookInfo } from "../../types/data";

type BookCardsProps = {
  books: BookInfo[];
  onSelect: (book: BookInfo) => void;
};

export default function BookCards(props: BookCardsProps) {
  const { books, onSelect } = props;
  const handleSelect = (bookId: string) => {
    alert(bookId);
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
          <Grid size={{ xs: 6, md: 3 }} sx={{ border: 2 }}>
            <BookCard {...book} onSelect={handleSelect}></BookCard>
          </Grid>
        ))}
      </Grid>
    </>
  );
}
