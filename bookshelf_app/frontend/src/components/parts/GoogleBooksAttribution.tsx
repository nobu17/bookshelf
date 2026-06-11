import Typography from "@mui/material/Typography";

import { isGoogleBooksImageUrl } from "../../libs/utils/image";

type GoogleBooksAttributionProps = {
  imageUrl?: string | null;
  align?: "left" | "center" | "right";
  compact?: boolean;
};

export default function GoogleBooksAttribution(
  props: GoogleBooksAttributionProps
) {
  const { imageUrl, align = "center", compact = false } = props;

  if (!isGoogleBooksImageUrl(imageUrl)) {
    return <></>;
  }

  return (
    <Typography
      component="div"
      variant="caption"
      sx={{
        color: "text.secondary",
        fontSize: compact ? "0.65rem" : "0.7rem",
        lineHeight: 1.2,
        mt: 0.25,
        textAlign: align,
        width: "100%",
      }}
    >
      Powered by Google
    </Typography>
  );
}
