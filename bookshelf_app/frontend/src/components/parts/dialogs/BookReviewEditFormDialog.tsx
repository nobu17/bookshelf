import Dialog from "@mui/material/Dialog";
import DialogActions from "@mui/material/DialogActions";
import DialogContent from "@mui/material/DialogContent";

import { BookInfo } from "../../../types/data";
import BookReviewEditForm, { ReviewEditInfo } from "../BookReviewEditForm";
import { DialogTitle } from "@mui/material";

type BookReviewEditFormDialogProps = {
  bookInfo: BookInfo | null;
  editItem: ReviewEditInfo | null;
  open: boolean;
  onClose: (item: ReviewEditInfo | null) => void;
  onBookEdit?: () => void;
  isBookEditEnabled?: boolean;
};

export default function BookReviewEditFormDialog(
  props: BookReviewEditFormDialogProps
) {
  if (props.editItem === null || props.bookInfo === null) {
    return <></>;
  }
  const onSubmit = (data: ReviewEditInfo) => {
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
            onBookEdit={props.onBookEdit}
            isBookEditEnabled={props.isBookEditEnabled}
          ></BookReviewEditForm>
        </DialogContent>
        <DialogActions></DialogActions>
      </Dialog>
    </>
  );
}
