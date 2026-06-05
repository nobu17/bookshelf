import {
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  IconButton,
  Stack,
  Tooltip,
} from "@mui/material";
import { GenericBookInfoWithReviews, Review } from "../../../types/data";
import CloseIcon from "@mui/icons-material/Close";
import EditIcon from "@mui/icons-material/Edit";
import OneBookReviewsDataGrid from "../OneBookReviewsDataGrid";

export type OneBookReviewsListDialogProps = {
  open: boolean;
  bookWithReviews?: GenericBookInfoWithReviews | null;
  onClose?: () => void;
  onEdit?: (review: Review) => void;
  onDelete?: (review: Review) => void;
  onAdd?: () => void;
  onBookEdit?: () => void;
  isBookEditEnabled?: boolean;
};

export default function OneBookReviewsListDialog(
  props: OneBookReviewsListDialogProps
) {
  const {
    open,
    bookWithReviews,
    onClose,
    onEdit,
    onDelete,
    onAdd,
    onBookEdit,
    isBookEditEnabled,
  } = props;
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
  const handleBookEdit = () => {
    if (!onBookEdit) {
      return;
    }
    onBookEdit();
  };

  return (
    <>
      <Dialog open={open} onClose={handleClose} fullScreen>
        <DialogTitle>レビュー 一覧</DialogTitle>
        <Stack
          direction="row"
          spacing={1}
          sx={() => ({
            position: "absolute",
            right: 8,
            top: 8,
          })}
        >
          {isBookEditEnabled ? (
            <Tooltip title="書籍マスタ編集">
              <IconButton
                aria-label="book-edit"
                color="primary"
                size="small"
                onClick={handleBookEdit}
              >
                <EditIcon />
              </IconButton>
            </Tooltip>
          ) : (
            <></>
          )}
          <Tooltip title="閉じる">
            <IconButton aria-label="close" onClick={handleClose}>
              <CloseIcon />
            </IconButton>
          </Tooltip>
        </Stack>
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
