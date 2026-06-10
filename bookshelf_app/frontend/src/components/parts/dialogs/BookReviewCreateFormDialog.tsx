import Dialog from "@mui/material/Dialog";
import DialogActions from "@mui/material/DialogActions";
import DialogContent from "@mui/material/DialogContent";
import { useEffect, useState } from "react";

import { ReviewState } from "../../../types/data";
import BookReviewEditForm, { ReviewEditInfo } from "../BookReviewEditForm";
import { DialogTitle, Snackbar } from "@mui/material";
import { BookCreateParameter } from "../../../libs/apis/books";
import BookTagEditor from "../BookTagEditor";
import useExistingBookTagsByIsbn from "../../../hooks/UseExistingBookTagsByIsbn";

export type BookReviewCreateFormDialogProps = {
  bookInfo: (BookCreateParameter & { imageUrl?: string | null }) | null;
  editItem: CreateParameter | null;
  open: boolean;
  onClose: (item: ReviewEditInfo | null, tagNames?: string[]) => void;
};

export type CreateParameter = {
  content: string;
  state: ReviewState;
  isDraft: boolean;
  completedAt: Date | null;
};

export default function BookReviewCreateFormDialog(
  props: BookReviewCreateFormDialogProps
) {
  const [tagNames, setTagNames] = useState<string[]>([]);
  const {
    tags: existingTags,
    error: existingTagsError,
  } = useExistingBookTagsByIsbn(
    props.bookInfo?.isbn13 ?? null,
    props.open && props.bookInfo !== null
  );

  useEffect(() => {
    if (props.open) {
      setTagNames([]);
    }
  }, [props.open]);

  if (props.editItem === null || props.bookInfo === null) {
    return <></>;
  }
  const onSubmit = (data: ReviewEditInfo) => {
    props.onClose(data, tagNames);
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
            bookActionContent={
              <BookTagEditor
                bookInfo={props.bookInfo}
                value={tagNames}
                readonlyTagNames={existingTags.map((tag) => tag.name)}
                onChange={setTagNames}
              />
            }
          ></BookReviewEditForm>
        </DialogContent>
        <DialogActions></DialogActions>
      </Dialog>
      <Snackbar
        open={Boolean(existingTagsError)}
        autoHideDuration={6000}
        message={existingTagsError?.message ?? ""}
      />
    </>
  );
}
