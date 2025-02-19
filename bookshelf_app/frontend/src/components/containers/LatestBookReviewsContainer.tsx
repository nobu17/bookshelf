import { useState } from "react";

import { CircularProgress } from "@mui/material";

import useLatestBookReviews from "../../hooks/dialogs/UseLatestBookReviews";
import BookCards from "../parts/BookCards";
import ErrorAlert from "../parts/ErrorAlert";
import BookReviewDialog from "../parts/dialogs/BookReviewDialog";
import { BookWithReviews } from "../../types/data";

type DialogState = {
  open: boolean;
  book?: BookWithReviews;
};

const initialState: DialogState = {
  open: false,
  book: undefined,
};

export default function LatestBookReviewsContainer() {
  const [dialogState, setDialogState] = useState<DialogState>(initialState);
  const { bookWithReviews, error, loading } = useLatestBookReviews();

  const handleClosed = () => {
    setDialogState(initialState);
  };

  if (loading) {
    return <CircularProgress />;
  }
  if (error) {
    return <ErrorAlert error={error} />;
  }
  return (
    <>
      <BookCards
        books={bookWithReviews}
        onSelect={(b) => {
          if (!b) return;
          setDialogState({ open: true, book: b });
        }}
      ></BookCards>
      <BookReviewDialog {...dialogState} onClose={handleClosed} />
    </>
  );
}
