import { Box, Button, Chip, Stack } from "@mui/material";
import LocalOfferIcon from "@mui/icons-material/LocalOffer";
import { useState } from "react";

import useBookTags from "../../hooks/UseBookTags";
import BookTagEditDialog from "./dialogs/BookTagEditDialog";

type BookInfoForDisplay = {
  isbn13: string;
  title: string;
  publisher: string;
  authors: string[];
  publishedAt: Date;
  imageUrl?: string | null;
};

type BookTagEditorProps = {
  bookInfo: BookInfoForDisplay;
  value: string[];
  readonlyTagNames?: string[];
  onChange: (tagNames: string[]) => void;
};

export default function BookTagEditor(props: BookTagEditorProps) {
  const { bookInfo, value, readonlyTagNames = [], onChange } = props;
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const { tags: tagOptions } = useBookTags();

  const handleApply = (tagNames: string[]) => {
    onChange(tagNames);
    setIsDialogOpen(false);
  };

  return (
    <>
      <Stack spacing={1.5}>
        <Button
          variant="outlined"
          startIcon={<LocalOfferIcon />}
          onClick={() => setIsDialogOpen(true)}
          sx={{ alignSelf: "stretch" }}
        >
          タグを付与
        </Button>
        {readonlyTagNames.length > 0 || value.length > 0 ? (
          <Box sx={{ display: "flex", gap: 1, flexWrap: "wrap" }}>
            {readonlyTagNames.map((tagName) => (
              <Chip key={tagName} label={tagName} size="small" />
            ))}
            {value.map((tagName) => (
              <Chip key={tagName} label={tagName} size="small" />
            ))}
          </Box>
        ) : (
          <></>
        )}
      </Stack>
      <BookTagEditDialog
        open={isDialogOpen}
        bookInfo={bookInfo}
        value={value}
        options={tagOptions}
        readonlyTagNames={readonlyTagNames}
        onApply={handleApply}
        onClose={() => setIsDialogOpen(false)}
      />
    </>
  );
}
