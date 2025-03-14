import {
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  IconButton,
} from "@mui/material";
import { GenericBookInfoWithReviews, Review } from "../../../types/data";
import CloseIcon from "@mui/icons-material/Close";
import OneBookReviewsDataGrid from "../OneBookReviewsDataGrid";

export type OneBookReviewsListDialogProps = {
  open: boolean;
  bookWithReviews?: GenericBookInfoWithReviews | null;
  onClose?: () => void;
  onEdit?: (review: Review) => void;
  onDelete?: (review: Review) => void;
  onAdd?: () => void;
};

export default function OneBookReviewsListDialog(
  props: OneBookReviewsListDialogProps
) {
  const { open, bookWithReviews, onClose, onEdit, onDelete, onAdd } = props;
  if (!bookWithReviews) {
    return <></>;
  }

  const handleClose = () => {
    if (!onClose) {
      return;
    }
    onClose();
  };

  const handleEdit = (review: Review) => {
    if (!onEdit) {
      return;
    }
    onEdit(review);
  };

  const handleDelete = (review: Review) => {
    if (!onDelete) {
      return;
    }
    onDelete(review);
  };

  const handleAdd = () => {
    if (!onAdd) {
      return;
    }
    onAdd();
  };

  return (
    <>
      <Dialog open={open} onClose={handleClose} fullScreen>
        <DialogTitle>レビュー 一覧</DialogTitle>
        <IconButton
          aria-label="close"
          onClick={handleClose}
          sx={() => ({
            position: "absolute",
            right: 8,
            top: 8,
          })}
        >
          <CloseIcon />
        </IconButton>
        <DialogContent>
          <OneBookReviewsDataGrid
            bookWithReviews={bookWithReviews}
            onEdit={handleEdit}
            onDelete={handleDelete}
            onAdd={handleAdd}
          />
        </DialogContent>
        <DialogActions></DialogActions>
      </Dialog>
    </>
  );
}
