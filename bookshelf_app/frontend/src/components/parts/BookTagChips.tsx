import { Box, Chip } from "@mui/material";
import { CSSProperties } from "react";

import { BookTag } from "../../types/data";

type BookTagChipsProps = {
  tags: BookTag[];
  maxVisible?: number;
  justifyContent?: CSSProperties["justifyContent"];
  onTagClick?: (tag: BookTag) => void;
};

export default function BookTagChips(props: BookTagChipsProps) {
  const { tags, maxVisible, justifyContent = "flex-start", onTagClick } = props;
  if (tags.length === 0) {
    return <></>;
  }

  const visibleTags = maxVisible ? tags.slice(0, maxVisible) : tags;
  const overflowCount = maxVisible ? tags.length - visibleTags.length : 0;

  return (
    <Box
      sx={{
        display: "flex",
        gap: 0.5,
        flexWrap: "wrap",
        justifyContent,
      }}
    >
      {visibleTags.map((tag) => (
        <Chip
          key={tag.id}
          label={tag.name}
          size="small"
          variant="outlined"
          onClick={onTagClick ? () => onTagClick(tag) : undefined}
        />
      ))}
      {overflowCount > 0 ? (
        <Chip label={`+${overflowCount}`} size="small" variant="outlined" />
      ) : (
        <></>
      )}
    </Box>
  );
}
