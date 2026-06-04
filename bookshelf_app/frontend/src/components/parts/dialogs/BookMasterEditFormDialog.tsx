import Dialog from "@mui/material/Dialog";
import DialogActions from "@mui/material/DialogActions";
import DialogContent from "@mui/material/DialogContent";
import DialogTitle from "@mui/material/DialogTitle";

import { BookInfo } from "../../../types/data";
import BookMasterEditForm, { BookMasterEditInfo } from "../BookMasterEditForm";

type BookMasterEditFormDialogProps = {
  bookInfo: BookInfo | null;
  open: boolean;
  onClose: (item: BookMasterEditInfo | null) => void;
};

export default function BookMasterEditFormDialog(
  props: BookMasterEditFormDialogProps
) {
  const { bookInfo, open, onClose } = props;
  if (bookInfo === null) {
    return <></>;
  }

  const handleSubmit = (data: BookMasterEditInfo) => {
    onClose(data);
  };
  const handleCancel = () => {
    onClose(null);
  };

  return (
    <Dialog open={open} fullScreen>
      <DialogTitle>書籍マスタ編集</DialogTitle>
      <DialogContent>
        <BookMasterEditForm
          bookInfo={bookInfo}
          onSubmit={handleSubmit}
          onCancel={handleCancel}
        />
      </DialogContent>
      <DialogActions></DialogActions>
    </Dialog>
  );
}
