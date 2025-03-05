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

export default function MyReviewsContainer() {
  const [isEditOpen, setIsEditOpen] = useState(false);
  const [editItem, setEditItem] = useState<Review | null>(null);
  const [book, setBook] = useState<BookInfo | null>(null);
  const { showConfirmDialog, renderConfirmDialog } = useConfirmDialog();
  const { setIsSpinnerOn } = useGlobalSpinnerContext();
  const { bookWithReviews, updateAsync, error, loading } = useMyBookReviews();

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
    if (await showConfirmDialog("確認", "削除を行ないます、よろしいですか？")) {
      alert(`delete bookId: ${bookId}, review: ${review}`);
    }
  };

  const handleEditClose = async (item: Review | null) => {
    setIsEditOpen(false);
    setEditItem(null);
    setBook(null);
    if (!item) {
      return;
    }
    await updateAsync(item.reviewId, item);
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
