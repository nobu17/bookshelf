import { Box, Chip } from "@mui/material";
import { CSSProperties, MouseEvent } from "react";

import { BookTag } from "../../types/data";

type BookTagChipsProps = {
  tags: BookTag[];
  maxVisible?: number;
  justifyContent?: CSSProperties["justifyContent"];
  onTagClick?: (tag: BookTag, event: MouseEvent<HTMLDivElement>) => void;
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
          sx={
            onTagClick
              ? {
                  cursor: "pointer",
                  bgcolor: "rgba(25, 118, 210, 0.08)",
                  borderColor: "rgba(25, 118, 210, 0.32)",
                  color: "primary.main",
                  fontWeight: 500,
                  "&:hover": {
                    bgcolor: "rgba(25, 118, 210, 0.16)",
                    borderColor: "primary.main",
                  },
                }
              : undefined
          }
          onClick={onTagClick ? (event) => onTagClick(tag, event) : undefined}
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
