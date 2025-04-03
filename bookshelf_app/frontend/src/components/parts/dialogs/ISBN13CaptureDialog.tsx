import { Dialog, DialogTitle, DialogContent, Button, Box } from "@mui/material";

import useISBN13Scan from "../../../hooks/UseISBN13Scan";
import { useEffect } from "react";
import ErrorAlert from "../ErrorAlert";

import styles from "./ISBN13CaptureDialog.module.css";

export type ISBN13CaptureDialogProps = {
  open: boolean;
  onClose: (isbn13: string | null) => void;
};

export default function ISBN13CaptureDialog(props: ISBN13CaptureDialogProps) {
  const handleDetected = (isbn13: string) => {
    onClose(isbn13);
  };
  const { onClose, open } = props;
  const { error, startCapture, stopCapture } =
    useISBN13Scan(handleDetected);

  useEffect(() => {
    if (open) {
      requestAnimationFrame(() => {
        startCapture("preview");
      });
    }
  }, [open, startCapture]);

  const handleCancel = async () => {
    await stopCapture();
    onClose(null);
  };

  return (
    <Dialog open={open}>
      <DialogTitle>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <span>書籍バーコード</span>
          <Button variant="contained" color="error" onClick={handleCancel}>
            キャンセル
          </Button>
        </Box>
      </DialogTitle>
      <DialogContent sx={{ maxHeight: "50vh", overflow: "hidden" }}>
        <div className={styles.camera} id="preview"></div>
        <ErrorAlert error={error}></ErrorAlert>
      </DialogContent>
    </Dialog>
  );
}
