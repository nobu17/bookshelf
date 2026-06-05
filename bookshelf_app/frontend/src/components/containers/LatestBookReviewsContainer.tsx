import { useState } from "react";

import { CircularProgress } from "@mui/material";

import useLatestBookReviews from "../../hooks/UseLatestBookReviews";
import BookCards from "../parts/BookCards";
import ErrorAlert from "../parts/ErrorAlert";
import BookReviewDialog from "../parts/dialogs/BookReviewDialog";
import { BookWithReviews } from "../../types/data";
import { useAuth } from "../contexts/AuthContext";
import useBookMasterEditDialog from "../../hooks/dialogs/UseBookMasterEditDialog";

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
  const { bookWithReviews, error, loading, loadAsync } = useLatestBookReviews();
  const {
    state: { isAuthorized },
  } = useAuth();
  const { openBookMasterEditDialog, renderBookMasterEditDialog } =
    useBookMasterEditDialog({
      onUpdated: async () => {
        await loadAsync();
      },
    });

  const handleClosed = () => {
    setDialogState(initialState);
  };
  const handleBookEdit = () => {
    openBookMasterEditDialog(dialogState.book);
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
      <BookReviewDialog
        {...dialogState}
        onClose={handleClosed}
        onBookEdit={handleBookEdit}
        isBookEditEnabled={isAuthorized}
      />
      {renderBookMasterEditDialog()}
    </>
  );
}
