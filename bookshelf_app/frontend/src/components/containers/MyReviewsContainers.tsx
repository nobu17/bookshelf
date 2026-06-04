import { useEffect, useState } from "react";

import { Snackbar } from "@mui/material";
import Grid from "@mui/material/Grid2";

import useMyBookReviews from "../../hooks/UseMyBookReviews";
import { useGlobalSpinnerContext } from "../contexts/GlobalSpinnerContext";
import ErrorAlert from "../parts/ErrorAlert";
import {
  BookInfo,
  BookWithReviews,
  copyReview,
  Review,
} from "../../types/data";
import { useConfirmDialog } from "../../hooks/dialogs/UseConfirmDialog";
import BookReviewEditFormDialog from "../parts/dialogs/BookReviewEditFormDialog";
import BookWithReviewsDataGrid from "../parts/BookWithReviewsDataGrid";
import { ReviewEditInfo } from "../parts/BookReviewEditForm";
import OneBookReviewsListDialogContainer from "./OneBookReviewsListDialogContainer";
import { useAuth } from "../contexts/AuthContext";
import BooksApi from "../../libs/apis/books";
import useAuthApi from "../../hooks/UseAuthApi";
import BookMasterEditFormDialog from "../parts/dialogs/BookMasterEditFormDialog";
import {
  BookMasterEditInfo,
  toBookUpdateParameter,
} from "../parts/BookMasterEditForm";

const bookApi = new BooksApi();

export default function MyReviewsContainer() {
  const [isEditOpen, setIsEditOpen] = useState(false);
  const [isListOpen, setIsListOpen] = useState(false);
  const [isBookEditOpen, setIsBookEditOpen] = useState(false);
  const [bookEditError, setBookEditError] = useState<Error | null>(null);
  const [editItem, setEditItem] = useState<Review | null>(null);
  const [book, setBook] = useState<BookInfo | null>(null);
  const [bookWithReview, setBookWithReview] = useState<BookWithReviews | null>(
    null
  );
  const { showConfirmDialog, renderConfirmDialog } = useConfirmDialog();
  const { setIsSpinnerOn } = useGlobalSpinnerContext();
  const { bookWithReviews, updateAsync, deleteAsync, loadAsync, error, loading } =
    useMyBookReviews();
  const {
    state: { isAuthorized },
  } = useAuth();
  useAuthApi(bookApi);

  const handleEdit = ({
    bookId,
    review,
  }: {
    bookId: string;
    review: Review;
  }) => {
    if (!review) {
      return;
    }
    const book = bookWithReviews.find((b) => b.bookId === bookId);
    if (!book) {
      console.error("not found book.", bookId);
      return;
    }
    setBook(book);
    const copied = copyReview(review);
    setEditItem(copied);
    setIsEditOpen(true);
  };

  const handleDelete = async ({
    bookId,
    review,
  }: {
    bookId: string;
    review: Review;
  }) => {
    const book = bookWithReviews.find((b) => b.bookId === bookId);
    if (!book) {
      console.error("not found book.", bookId);
      return;
    }
    if (
      await showConfirmDialog(
        "確認",
        `[${book.title}]の削除を行ないます、よろしいですか？`
      )
    ) {
      await deleteAsync(review.reviewId);
    }
  };

  const handleSelect = (bookWithReview: BookWithReviews) => {
    setBookWithReview(bookWithReview);
    setIsListOpen(true);
  };

  const handleSelectClose = async () => {
    setBookWithReview(null);
    setIsListOpen(false);
    await loadAsync();
  };

  const handleEditClose = async (item: ReviewEditInfo | null) => {
    setIsEditOpen(false);
    setEditItem(null);
    setBook(null);
    if (!item) {
      return;
    }
    if (!editItem || !book) {
      return;
    }
    const newItem = { ...editItem, ...item };
    await updateAsync(book.bookId, newItem.reviewId, newItem);
  };
  const handleBookEdit = () => {
    setBookEditError(null);
    setIsBookEditOpen(true);
  };
  const handleBookEditClose = async (item: BookMasterEditInfo | null) => {
    if (!item || !book) {
      setIsBookEditOpen(false);
      return;
    }
    try {
      const updated = await bookApi.update(book.bookId, toBookUpdateParameter(item));
      setBook(updated.data);
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

  useEffect(() => {
    setIsSpinnerOn(loading);
  }, [setIsSpinnerOn, loading]);

  if (error) {
    return <ErrorAlert error={error} />;
  }

  return (
    <>
      <Grid container spacing={2} sx={{ justifyContent: "center" }}>
        <Grid size={{ xs: 12, md: 10 }}>
          <BookWithReviewsDataGrid
            reviews={bookWithReviews}
            onEdit={handleEdit}
            onDelete={handleDelete}
            onSelect={handleSelect}
          />
        </Grid>
      </Grid>
      <BookReviewEditFormDialog
        open={isEditOpen}
        editItem={editItem}
        bookInfo={book}
        onClose={handleEditClose}
        onBookEdit={handleBookEdit}
        isBookEditEnabled={isAuthorized}
      />
      <BookMasterEditFormDialog
        open={isBookEditOpen}
        bookInfo={book}
        onClose={handleBookEditClose}
      />
      <OneBookReviewsListDialogContainer
        open={isListOpen}
        bookId={bookWithReview?.bookId ?? ""}
        onClose={handleSelectClose}
      />
      <Snackbar
        anchorOrigin={{ vertical: "top", horizontal: "center" }}
        open={bookEditError ? true : false}
        autoHideDuration={6000}
        message={bookEditError ? bookEditError.message : ""}
      />
      {renderConfirmDialog()}
    </>
  );
}
