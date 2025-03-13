import { useEffect, useState } from "react";

import Grid from "@mui/material/Grid2";

import useMyBookReviews from "../../hooks/UseMyBookReviews";
import ReviewEditDataGrid from "../parts/ReviewEditDataGrid";
import { useGlobalSpinnerContext } from "../contexts/GlobalSpinnerContext";
import ErrorAlert from "../parts/ErrorAlert";
import { BookInfo, copyReview, Review } from "../../types/data";
import { useConfirmDialog } from "../../hooks/dialogs/UseConfirmDialog";
import BookReviewEditFormDialog from "../parts/dialogs/BookReviewEditFormDialog";
import BookWithReviewsDataGrid from "../parts/BookWithReviewsDataGrid";
import { ReviewEditInfo } from "../parts/BookReviewEditForm";

export default function MyReviewsContainer() {
  const [isEditOpen, setIsEditOpen] = useState(false);
  const [editItem, setEditItem] = useState<Review | null>(null);
  const [book, setBook] = useState<BookInfo | null>(null);
  const { showConfirmDialog, renderConfirmDialog } = useConfirmDialog();
  const { setIsSpinnerOn } = useGlobalSpinnerContext();
  const { bookWithReviews, updateAsync, deleteAsync, error, loading } =
    useMyBookReviews();

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
    if (await showConfirmDialog("確認", `[${book.title}]の削除を行ないます、よろしいですか？`)) {
      await deleteAsync(review.reviewId);
    }
  };

  const handleEditClose = async (item: ReviewEditInfo | null) => {
    setIsEditOpen(false);
    setEditItem(null);
    setBook(null);
    if (!item) {
      return;
    }
    if (!editItem) {
      return;
    }
    const newItem = { ...editItem, ...item };
    await updateAsync(newItem.reviewId, newItem);
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
          />
        </Grid>

        <Grid size={{ xs: 12, md: 10 }}>
          <ReviewEditDataGrid
            reviews={bookWithReviews}
            onDelete={handleDelete}
            onEdit={handleEdit}
          />
        </Grid>
      </Grid>
      <BookReviewEditFormDialog
        open={isEditOpen}
        editItem={editItem}
        bookInfo={book}
        onClose={handleEditClose}
      />
      {renderConfirmDialog()}
    </>
  );
}
