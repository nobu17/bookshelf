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
import { ValidationError } from "../../types/errors";
import { useAuth } from "../contexts/AuthContext";
import useBookMasterEditDialog from "../../hooks/dialogs/UseBookMasterEditDialog";

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
    loadAsync,
  } = useMySpecificBookReviews();
  const {
    state: { isAuthorized },
  } = useAuth();
  const { setIsSpinnerOn } = useGlobalSpinnerContext();
  const { showConfirmDialog, renderConfirmDialog } = useConfirmDialog();
  const [isEditOpen, setIsEditOpen] = useState(false);
  const [editItem, setEditItem] = useState<Review | null>(null);
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [validationError, setValidationError] =
    useState<ValidationError | null>(null);
  const [createItem, setCreateItem] = useState<ReviewEditInfo | null>(null);
  const {
    openBookMasterEditDialog,
    isBookMasterEditLoading,
    renderBookMasterEditDialog,
  } = useBookMasterEditDialog({
    onUpdated: async () => {
      await loadAsync();
    },
  });

  useEffect(() => {
    setIsSpinnerOn(loading || isBookMasterEditLoading);
  }, [loading, isBookMasterEditLoading, setIsSpinnerOn]);

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
    let validationErr: ValidationError | null = null;
    try {
      if (!item || !bookWithReviews) {
        return;
      }
      validationErr = await createAsync(bookWithReviews.bookId, item);
      setValidationError(validationErr);
    } finally {
      // validation error case, not close the dialog.
      if (validationErr === null) {
        setIsCreateOpen(false);
        setCreateItem(null);
        setValidationError(null);
      }
    }
  };
  const handleEdit = async (review: Review) => {
    const copied = copyReview(review);
    setEditItem(copied);
    setIsEditOpen(true);
  };
  const handleEditClose = async (item: ReviewEditInfo | null) => {
    let validationErr: ValidationError | null = null;
    try {
      if (!item || !bookWithReviews) {
        return;
      }
      if (!editItem) {
        return;
      }
      const newItem = { ...editItem, ...item };
      validationErr = await updateAsync(
        bookWithReviews.bookId,
        newItem.reviewId,
        newItem
      );
      setValidationError(validationErr);
    } finally {
      // validation error case, not close the dialog.
      if (validationErr === null) {
        setIsEditOpen(false);
        setEditItem(null);
        setValidationError(null);
      }
    }
  };
  const handleBookEdit = () => {
    openBookMasterEditDialog(bookWithReviews);
  };

  return (
    <>
      <Snackbar
        anchorOrigin={{ vertical: "top", horizontal: "center" }}
        open={error ? true : false}
        autoHideDuration={6000}
        message={error ? error.message : ""}
      />
      <Snackbar
        anchorOrigin={{ vertical: "top", horizontal: "center" }}
        open={validationError ? true : false}
        autoHideDuration={6000}
        message={validationError ? validationError.message : ""}
      />
      <OneBookReviewsListDialog
        open={open}
        bookWithReviews={bookWithReviews}
        onClose={onClose}
        onEdit={handleEdit}
        onDelete={handleDelete}
        onAdd={handleAdd}
        onBookEdit={handleBookEdit}
        isBookEditEnabled={isAuthorized}
      />
      {renderBookMasterEditDialog()}
      <BookReviewEditFormDialog
        open={isEditOpen}
        editItem={editItem}
        bookInfo={bookWithReviews}
        onClose={handleEditClose}
        onBookEdit={handleBookEdit}
        isBookEditEnabled={isAuthorized}
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
