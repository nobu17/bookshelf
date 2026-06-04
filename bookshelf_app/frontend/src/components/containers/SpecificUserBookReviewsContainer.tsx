import { useState } from "react";

import { CircularProgress, Snackbar, Typography } from "@mui/material";

import useSpecificUserBookReviews from "../../hooks/UseSpecificUserBookReviews";
import BookCards from "../parts/BookCards";
import ErrorAlert from "../parts/ErrorAlert";
import BookReviewDialog from "../parts/dialogs/BookReviewDialog";
import { BookWithReviews } from "../../types/data";
import BookCardsDisplayOptions from "../parts/BookCardsDisplayOptions";
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

type LatestBookReviewsContainerProps = {
  userId: string;
};

export default function SpecificUserBookReviewsContainer(
  props: LatestBookReviewsContainerProps
) {
  const { userId } = props;
  const [dialogState, setDialogState] = useState<DialogState>(initialState);
  const [isBookEditOpen, setIsBookEditOpen] = useState(false);
  const [bookEditError, setBookEditError] = useState<Error | null>(null);
  const { filteredReviews, displayOption, setDisplayOption, userName, error, loading, loadAsync } =
    useSpecificUserBookReviews(userId);
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
      await loadAsync(userId);
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
      <Typography variant="h6" align="center" gutterBottom>
        {userName}さんの本棚
      </Typography>
      <BookCardsDisplayOptions option={displayOption} onChange={setDisplayOption} />
      <BookCards
        books={filteredReviews}
        isRibbonRender={true}
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
