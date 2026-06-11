import {
  Box,
  Button,
  Chip,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Stack,
  Typography,
} from "@mui/material";
import { useEffect, useState } from "react";

import { BookTag } from "../../../types/data";
import { dateToString } from "../../../libs/utils/date";
import { getBookInfoImageUrl, getFallbackImageUrl } from "../../../libs/utils/image";
import { validateBookTagNames } from "../../../libs/services/bookTags";
import BookTagInput from "../BookTagInput";
import GoogleBooksAttribution from "../GoogleBooksAttribution";

type BookInfoForDisplay = {
  isbn13: string;
  title: string;
  publisher: string;
  authors: string[];
  publishedAt: Date;
  imageUrl?: string | null;
};

type BookTagEditDialogProps = {
  open: boolean;
  bookInfo: BookInfoForDisplay;
  value: string[];
  options: BookTag[];
  readonlyTagNames?: string[];
  onApply: (tagNames: string[]) => void;
  onClose: () => void;
};

export default function BookTagEditDialog(props: BookTagEditDialogProps) {
  const {
    open,
    bookInfo,
    value,
    options,
    readonlyTagNames = [],
    onApply,
    onClose,
  } = props;
  const [draftTagNames, setDraftTagNames] = useState<string[]>(value);
  const errorMessage = validateBookTagNames(draftTagNames);

  useEffect(() => {
    if (open) {
      setDraftTagNames(value);
    }
  }, [open, value]);

  const handleApply = () => {
    if (errorMessage) {
      return;
    }
    onApply(excludeReadonlyTags(draftTagNames, readonlyTagNames));
  };
  const handleChange = (tagNames: string[]) => {
    setDraftTagNames(excludeReadonlyTags(tagNames, readonlyTagNames));
  };

  return (
    <Dialog open={open} onClose={onClose} fullWidth maxWidth="sm">
      <DialogTitle>タグを付与</DialogTitle>
      <DialogContent>
        <Stack spacing={3} sx={{ pt: 1 }}>
          <Stack direction="row" spacing={2} alignItems="center">
            <Box sx={{ flexShrink: 0, textAlign: "center", width: 80 }}>
              <Box
                component="img"
                sx={{
                  width: 72,
                  height: 88,
                  objectFit: "contain",
                }}
                src={getBookInfoImageUrl(bookInfo)}
                onError={(e) => {
                  e.currentTarget.src = getFallbackImageUrl();
                }}
              />
              <GoogleBooksAttribution imageUrl={bookInfo.imageUrl} compact />
            </Box>
            <Typography variant="body2" align="left">
              書籍名：{bookInfo.title}
              <br />
              出版社：{bookInfo.publisher}
              <br />
              著者：{bookInfo.authors.join(": ")}
              <br />
              出版年：{dateToString(bookInfo.publishedAt)}
            </Typography>
          </Stack>
          {readonlyTagNames.length > 0 ? (
            <Stack spacing={1}>
              <Typography variant="subtitle2">この本のタグ</Typography>
              <Box sx={{ display: "flex", gap: 1, flexWrap: "wrap" }}>
                {readonlyTagNames.map((tagName) => (
                  <Chip key={tagName} label={tagName} size="small" />
                ))}
              </Box>
            </Stack>
          ) : (
            <></>
          )}
          <BookTagInput
            label={readonlyTagNames.length > 0 ? "追加するタグ" : "タグ"}
            value={draftTagNames}
            options={options.filter(
              (tag) => !readonlyTagNames.includes(tag.name)
            )}
            onChange={handleChange}
          />
        </Stack>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>キャンセル</Button>
        <Button
          variant="contained"
          onClick={handleApply}
          disabled={Boolean(errorMessage)}
        >
          反映
        </Button>
      </DialogActions>
    </Dialog>
  );
}

const excludeReadonlyTags = (
  tagNames: string[],
  readonlyTagNames: string[]
): string[] => {
  return tagNames.filter((tagName) => !readonlyTagNames.includes(tagName));
};
