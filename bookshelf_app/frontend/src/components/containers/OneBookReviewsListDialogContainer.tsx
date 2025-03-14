import { useEffect, useState } from "react";
import useMySpecificBookReviews from "../../hooks/UseMySpecificBookReviews";
import OneBookReviewsListDialog from "../parts/dialogs/OneBookReviewsListDialog";
import { useGlobalSpinnerContext } from "../contexts/GlobalSpinnerContext";
import { Snackbar } from "@mui/material";
import { useConfirmDialog } from "../../hooks/dialogs/UseConfirmDialog";
import { copyReview, Review, ReviewStateDef } from "../../types/data";
import BookReviewEditFormDialog from "../parts/dialogs/BookReviewEditFormDialog";
import { ReviewEditInfo } from "../parts/BookReviewEditForm";
import BookReviewCreateFormDialog from "../parts/dialogs/BookReviewCreateFormDialog";

type OneBookReviewsListDialogContainerProps = {
  open: boolean;
  bookId: string;
  onClose?: () => void;
  onEditError?: (error: Error | undefined) => void;
  onError?: (error: Error | undefined) => void;
};

export default function OneBookReviewsListDialogContainer(
  props: OneBookReviewsListDialogContainerProps
) {
  const { open, bookId, onError, onClose } = props;
  const {
    bookWithReviews,
    deleteAsync,
    updateAsync,
    createAsync,
    loading,
    setBookId,
    error,
  } = useMySpecificBookReviews();
  const { setIsSpinnerOn } = useGlobalSpinnerContext();
  const { showConfirmDialog, renderConfirmDialog } = useConfirmDialog();
  const [isEditOpen, setIsEditOpen] = useState(false);
  const [editItem, setEditItem] = useState<Review | null>(null);
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [createItem, setCreateItem] = useState<ReviewEditInfo | null>(null);

  useEffect(() => {
    setIsSpinnerOn(loading);
  }, [loading, setIsSpinnerOn]);

  useEffect(() => {
    setBookId(bookId);
  }, [bookId, setBookId]);

  useEffect(() => {
    if (onError) {
      if (error) {
        onError(error);
      }
    }
  }, [error, onError]);

  const handleDelete = async (review: Review) => {
    if (await showConfirmDialog("確認", `削除を行ないます、よろしいですか？`)) {
      await deleteAsync(review.reviewId);
    }
  };
  const handleAdd = () => {
    const initial = {
      content: "",
      isDraft: false,
      state: ReviewStateDef.Completed,
      completedAt: new Date(),
    };
    setCreateItem(initial);
    setIsCreateOpen(true);
  };
  const handleAddClose = async (item: ReviewEditInfo | null) => {
    setIsCreateOpen(false);
    setCreateItem(null);
    if (!item || !bookWithReviews) {
      return;
    }
    await createAsync(bookWithReviews.bookId, item);
  };
  const handleEdit = async (review: Review) => {
    const copied = copyReview(review);
    setEditItem(copied);
    setIsEditOpen(true);
  };
  const handleEditClose = async (item: ReviewEditInfo | null) => {
    setIsEditOpen(false);
    setEditItem(null);
    if (!item) {
      return;
    }
    if (!editItem) {
      return;
    }
    const newItem = { ...editItem, ...item };
    await updateAsync(newItem.reviewId, newItem);
  };

  return (
    <>
      <Snackbar
        open={error ? true : false}
        autoHideDuration={6000}
        message={error ? error.message : ""}
      />
      <OneBookReviewsListDialog
        open={open}
        bookWithReviews={bookWithReviews}
        onClose={onClose}
        onEdit={handleEdit}
        onDelete={handleDelete}
        onAdd={handleAdd}
      />
      <BookReviewEditFormDialog
        open={isEditOpen}
        editItem={editItem}
        bookInfo={bookWithReviews}
        onClose={handleEditClose}
      />
      <BookReviewCreateFormDialog
        open={isCreateOpen}
        bookInfo={bookWithReviews}
        editItem={createItem}
        onClose={handleAddClose}
      />
      {renderConfirmDialog()}
    </>
  );
}
