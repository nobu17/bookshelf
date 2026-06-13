import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  TextField,
} from "@mui/material";
import { useEffect, useState } from "react";

import { BookTag } from "../../../types/data";
import {
  MAX_BOOK_TAG_NAME_LENGTH,
  normalizeBookTagName,
} from "../../../libs/services/bookTags";

type TagMasterEditDialogProps = {
  open: boolean;
  tag: BookTag | null;
  onSubmit: (name: string) => void;
  onClose: () => void;
};

export default function TagMasterEditDialog(props: TagMasterEditDialogProps) {
  const { open, tag, onSubmit, onClose } = props;
  const [name, setName] = useState("");
  const normalizedName = normalizeBookTagName(name);
  const errorMessage = validateTagName(normalizedName);

  useEffect(() => {
    if (open) {
      setName(tag?.name ?? "");
    }
  }, [open, tag]);

  const handleSubmit = () => {
    if (errorMessage) {
      return;
    }
    onSubmit(normalizedName);
  };

  return (
    <Dialog open={open} onClose={onClose} fullWidth maxWidth="xs">
      <DialogTitle>{tag ? "タグ編集" : "タグ作成"}</DialogTitle>
      <DialogContent sx={{ pt: 1 }}>
        <TextField
          autoFocus
          fullWidth
          label="タグ名"
          value={name}
          error={Boolean(errorMessage)}
          helperText={errorMessage ?? `${MAX_BOOK_TAG_NAME_LENGTH}文字以内`}
          onChange={(event) => setName(event.target.value)}
        />
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>キャンセル</Button>
        <Button
          variant="contained"
          onClick={handleSubmit}
          disabled={Boolean(errorMessage)}
        >
          保存
        </Button>
      </DialogActions>
    </Dialog>
  );
}

const validateTagName = (name: string): string | null => {
  if (!name) {
    return "タグ名は必須です。";
  }
  if (name.length > MAX_BOOK_TAG_NAME_LENGTH) {
    return `タグ名は最大${MAX_BOOK_TAG_NAME_LENGTH}文字です。`;
  }
  return null;
};
