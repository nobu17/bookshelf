import { Box, Chip, Typography } from "@mui/material";

import { BookTag } from "../../types/data";

type SelectedTagFilterBarProps = {
  tag: BookTag | null;
  resultCount: number;
  onClear: () => void;
};

export default function SelectedTagFilterBar(props: SelectedTagFilterBarProps) {
  const { tag, resultCount, onClear } = props;

  if (!tag) {
    return <></>;
  }

  return (
    <Box
      sx={{
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        flexWrap: "wrap",
        gap: 1,
        mb: 2,
      }}
    >
      <Typography variant="body2" color="text.secondary">
        タグで絞り込み
      </Typography>
      <Chip label={tag.name} color="primary" onDelete={onClear} />
      <Typography variant="body2" color="text.secondary">
        {resultCount}件
      </Typography>
    </Box>
  );
}
