import Dialog from "@mui/material/Dialog";
import DialogActions from "@mui/material/DialogActions";
import DialogContent from "@mui/material/DialogContent";

import { BookInfo, Review } from "../../../types/data";
import BookReviewEditForm from "../BookReviewEditForm";
import { DialogTitle } from "@mui/material";

type BookReviewEditFormDialogProps = {
  bookInfo: BookInfo | null;
  editItem: Review | null;
  open: boolean;
  onClose: (item: Review | null) => void;
};

export default function BookReviewEditFormDialog(
  props: BookReviewEditFormDialogProps
) {
  if (props.editItem === null || props.bookInfo === null) {
    return <></>;
  }
  const onSubmit = (data: Review) => {
    props.onClose(data);
  };
  const onCancel = () => {
    props.onClose(null);
  };

  return (
    <>
      <Dialog open={props.open} fullScreen>
        <DialogTitle>レビュー編集</DialogTitle>
        <DialogContent>
          <BookReviewEditForm
            editItem={props.editItem}
            bookInfo={props.bookInfo}
            onSubmit={onSubmit}
            onCancel={onCancel}
          ></BookReviewEditForm>
        </DialogContent>
        <DialogActions></DialogActions>
      </Dialog>
    </>
  );
}
