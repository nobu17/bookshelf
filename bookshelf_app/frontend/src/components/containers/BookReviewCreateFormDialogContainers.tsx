import { useEffect, useState } from "react";
import { useGlobalSpinnerContext } from "../contexts/GlobalSpinnerContext";
import BookReviewCreateFormDialog, {
  BookReviewCreateFormDialogProps,
} from "../parts/dialogs/BookReviewCreateFormDialog";
import { Snackbar } from "@mui/material";
import { ReviewEditInfo } from "../parts/BookReviewEditForm";
import useBookAndReviewCreate from "../../hooks/UseBookAndReviewCreate";
import { ValidationError } from "../../types/errors";

type BookReviewCreateFormDialogContainersProps =
  BookReviewCreateFormDialogProps & {};

export default function BookReviewCreateFormDialogContainers(
  props: BookReviewCreateFormDialogContainersProps
) {
  const { bookInfo } = props;
  const { loading, error, createAsync } = useBookAndReviewCreate();
  const [validationError, setValidationError] =
    useState<ValidationError | null>(null);
  const { setIsSpinnerOn } = useGlobalSpinnerContext();

  useEffect(() => {
    setIsSpinnerOn(loading);
  }, [setIsSpinnerOn, loading]);

  const hasError = (): boolean => {
    if (error) {
      return true;
    }
    if (validationError) {
      return true;
    }
    return false;
  };
  const errorMessage = (): string => {
    if (error) {
      return error.message;
    }
    if (validationError) {
      return validationError.message;
    }
    return "";
  };

  const handleClose = async (item: ReviewEditInfo | null) => {
    setValidationError(null);
    // cancel or unexpected
    if (!item || !bookInfo) {
      props.onClose(item);
      return;
    }
    const validationErr = await createAsync(bookInfo, item);
    setValidationError(validationErr);
    if (validationErr) {
      // dialog not close when validation error
      return;
    }
    props.onClose(item);
  };

  return (
    <>
      <Snackbar
        open={hasError()}
        autoHideDuration={6000}
        message={errorMessage()}
      />
      <BookReviewCreateFormDialog {...props} onClose={handleClose} />
    </>
  );
}
