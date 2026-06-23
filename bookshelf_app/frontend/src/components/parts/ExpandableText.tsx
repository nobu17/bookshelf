import { Button, Stack, Typography } from "@mui/material";
import { MouseEvent, useState } from "react";

type ExpandableTextProps = {
  text: string;
  maxLength?: number;
  maxLines?: number;
};

export default function ExpandableText(props: ExpandableTextProps) {
  const { text, maxLength = 100, maxLines = 4 } = props;
  const [expanded, setExpanded] = useState(false);
  const lineCount = text.split("\n").length;
  const shouldTruncate = text.length > maxLength || lineCount > maxLines;

  const handleToggle = (event: MouseEvent<HTMLButtonElement>) => {
    event.stopPropagation();
    setExpanded((current) => !current);
  };

  return (
    <Stack spacing={0.5} alignItems="flex-start">
      <Typography
        color="text.secondary"
        sx={{
          lineHeight: 1.85,
          whiteSpace: "pre-line",
          ...(shouldTruncate && !expanded
            ? {
                display: "-webkit-box",
                WebkitBoxOrient: "vertical",
                WebkitLineClamp: maxLines,
                overflow: "hidden",
              }
            : {}),
        }}
      >
        {text}
      </Typography>
      {shouldTruncate ? (
        <Button size="small" onClick={handleToggle} sx={{ px: 0 }}>
          {expanded ? "閉じる" : "続きを見る"}
        </Button>
      ) : (
        <></>
      )}
    </Stack>
  );
}
