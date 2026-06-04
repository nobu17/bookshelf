import { useState } from "react";

import { CircularProgress, Snackbar } from "@mui/material";

import useLatestBookReviews from "../../hooks/UseLatestBookReviews";
import BookCards from "../parts/BookCards";
import ErrorAlert from "../parts/ErrorAlert";
import BookReviewDialog from "../parts/dialogs/BookReviewDialog";
import { BookWithReviews } from "../../types/data";
import { useAuth } from "../contexts/AuthContext";
import BooksApi from "../../libs/apis/books";
import useAuthApi from "../../hooks/UseAuthApi";
import BookMasterEditFormDialog from "../parts/dialogs/BookMasterEditFormDialog";
import {
  BookMasterEditInfo,
  toBookUpdateParameter,
} from "../parts/BookMasterEditForm";

type DialogState = {
  open: boolean;
  book?: BookWithReviews;
};

const initialState: DialogState = {
  open: false,
  book: undefined,
};

const bookApi = new BooksApi();

export default function LatestBookReviewsContainer() {
  const [dialogState, setDialogState] = useState<DialogState>(initialState);
  const [isBookEditOpen, setIsBookEditOpen] = useState(false);
  const [bookEditError, setBookEditError] = useState<Error | null>(null);
  const { bookWithReviews, error, loading, loadAsync } = useLatestBookReviews();
  const {
    state: { isAuthorized },
  } = useAuth();
  useAuthApi(bookApi);

  const handleClosed = () => {
    setDialogState(initialState);
  };
  const handleBookEdit = () => {
    setBookEditError(null);
    setIsBookEditOpen(true);
  };
  const handleBookEditClose = async (item: BookMasterEditInfo | null) => {
    if (!item || !dialogState.book) {
      setIsBookEditOpen(false);
      return;
    }
    try {
      await bookApi.update(dialogState.book.bookId, toBookUpdateParameter(item));
      await loadAsync();
      setBookEditError(null);
      setIsBookEditOpen(false);
    } catch (e: unknown) {
      if (e instanceof Error) {
        setBookEditError(e);
        return;
      }
      setBookEditError(new Error("unexpected error."));
    }
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
      <BookMasterEditFormDialog
        open={isBookEditOpen}
        bookInfo={dialogState.book ?? null}
        onClose={handleBookEditClose}
      />
      <Snackbar
        anchorOrigin={{ vertical: "top", horizontal: "center" }}
        open={bookEditError ? true : false}
        autoHideDuration={6000}
        message={bookEditError ? bookEditError.message : ""}
      />
    </>
  );
}
