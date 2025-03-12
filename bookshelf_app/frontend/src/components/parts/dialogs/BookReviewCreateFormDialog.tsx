import Dialog from "@mui/material/Dialog";
import DialogActions from "@mui/material/DialogActions";
import DialogContent from "@mui/material/DialogContent";

import { ReviewState } from "../../../types/data";
import BookReviewEditForm, { ReviewEditInfo } from "../BookReviewEditForm";
import { DialogTitle } from "@mui/material";
import { NdlBook } from "../../../types/ndls";

type BookReviewCreateFormDialogProps = {
  bookInfo: NdlBook | null;
  editItem: CreateParameter | null;
  open: boolean;
  onClose: (item: ReviewEditInfo | null) => void;
};

type CreateParameter = {
  content: string;
  state: ReviewState;
  isDraft: boolean;
  completedAt: Date | null;
};

export default function BookReviewCreateFormDialog(
  props: BookReviewCreateFormDialogProps
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
        <DialogTitle>レビュー投稿</DialogTitle>
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
