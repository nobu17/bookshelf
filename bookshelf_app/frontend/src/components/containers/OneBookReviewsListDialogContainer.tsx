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
import BooksApi from "../../libs/apis/books";
import useAuthApi from "../../hooks/UseAuthApi";
import BookMasterEditFormDialog from "../parts/dialogs/BookMasterEditFormDialog";
import {
  BookMasterEditInfo,
  toBookUpdateParameter,
} from "../parts/BookMasterEditForm";

type OneBookReviewsListDialogContainerProps = {
  open: boolean;
  bookId: string;
  onClose?: () => void;
  onEditError?: (error: Error | undefined) => void;
  onError?: (error: Error | undefined) => void;
};

const bookApi = new BooksApi();

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
  useAuthApi(bookApi);
  const {
    state: { isAuthorized },
  } = useAuth();
  const { setIsSpinnerOn } = useGlobalSpinnerContext();
  const { showConfirmDialog, renderConfirmDialog } = useConfirmDialog();
  const [isEditOpen, setIsEditOpen] = useState(false);
  const [editItem, setEditItem] = useState<Review | null>(null);
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [isBookEditOpen, setIsBookEditOpen] = useState(false);
  const [bookEditError, setBookEditError] = useState<Error | null>(null);
  const [isBookEditLoading, setIsBookEditLoading] = useState(false);
  const [validationError, setValidationError] =
    useState<ValidationError | null>(null);
  const [createItem, setCreateItem] = useState<ReviewEditInfo | null>(null);

  useEffect(() => {
    setIsSpinnerOn(loading || isBookEditLoading);
  }, [loading, isBookEditLoading, setIsSpinnerOn]);

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
    setBookEditError(null);
    setIsBookEditOpen(true);
  };
  const handleBookEditClose = async (item: BookMasterEditInfo | null) => {
    if (!item || !bookWithReviews) {
      setIsBookEditOpen(false);
      return;
    }
    setIsBookEditLoading(true);
    try {
      await bookApi.update(bookWithReviews.bookId, toBookUpdateParameter(item));
      await loadAsync();
      setBookEditError(null);
      setIsBookEditOpen(false);
    } catch (e: unknown) {
      if (e instanceof Error) {
        setBookEditError(e);
        return;
      }
      setBookEditError(new Error("unexpected error."));
    } finally {
      setIsBookEditLoading(false);
    }
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
      <Snackbar
        anchorOrigin={{ vertical: "top", horizontal: "center" }}
        open={bookEditError ? true : false}
        autoHideDuration={6000}
        message={bookEditError ? bookEditError.message : ""}
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
      <BookMasterEditFormDialog
        open={isBookEditOpen}
        bookInfo={bookWithReviews}
        onClose={handleBookEditClose}
      />
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
