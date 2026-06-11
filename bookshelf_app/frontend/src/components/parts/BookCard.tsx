import Card from "@mui/material/Card";
import CardActionArea from "@mui/material/CardActionArea";
import CardMedia from "@mui/material/CardMedia";
import Typography from "@mui/material/Typography";
import Box from "@mui/material/Box";
import { MouseEvent } from "react";

import styles from "./BookCard.module.css";
import { BookTag, BookWithReviews } from "../../types/data";
import { getBookInfoImageUrl, getFallbackImageUrl } from "../../libs/utils/image";
import BookCardRibbon from "./BookCardRibbon";
import BookTagChips from "./BookTagChips";
import GoogleBooksAttribution from "./GoogleBooksAttribution";

type BookCardProps = {
  book: BookWithReviews;
  isRibbonRender?: boolean;
  onSelect: (bookId: string) => void;
  onTagClick?: (tag: BookTag) => void;
};

export default function BookCard(props: BookCardProps) {
  const { bookId, title } = props.book;
  const { book, isRibbonRender } = props;
  const { onSelect, onTagClick } = props;
  const handleTagClick = (tag: BookTag, event: MouseEvent<HTMLDivElement>) => {
    event.stopPropagation();
    onTagClick?.(tag);
  };
  return (
    <Card
      variant="outlined"
      sx={{
        width: "100%",
        borderRadius: "8px",
        borderColor: "rgba(31, 41, 55, 0.16)",
        backgroundColor: "#fcfcfd",
        boxShadow: "0 1px 2px rgba(0, 0, 0, 0.04)",
        transition:
          "border-color 160ms ease, box-shadow 160ms ease, transform 160ms ease",
        "&:hover": {
          borderColor: "rgba(25, 118, 210, 0.42)",
          boxShadow: "0 6px 16px rgba(0, 0, 0, 0.12)",
          transform: "translateY(-2px)",
        },
      }}
    >
      <CardActionArea
        className={styles.box}
        sx={{
          height: "100%",
          minHeight: 304,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "flex-start",
          px: 1.25,
          pb: 1.25,
        }}
        onClick={() => onSelect(bookId)}
      >
        {isRibbonRender ? <BookCardRibbon reviews={book.reviews} /> : <></>}
        <Box
          sx={{
            width: "100%",
            height: 208,
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            pt: 1.5,
            pb: 1,
          }}
        >
          <CardMedia
            component="img"
            sx={{
              maxHeight: 182,
              width: "100%",
              objectFit: "contain",
              filter: "drop-shadow(0 4px 8px rgba(0, 0, 0, 0.16))",
            }}
            image={getBookInfoImageUrl(book)}
            onError={(e) => {
              e.currentTarget.src = getFallbackImageUrl();
            }}
          />
          <GoogleBooksAttribution imageUrl={book.imageUrl} compact />
        </Box>
        <Box
          sx={{
            width: "100%",
            textAlign: "left",
            px: 0.5,
            minHeight: 58,
            display: "flex",
            alignItems: "center",
            justifyContent: "flex-start",
          }}
        >
          <Typography
            sx={{
              fontWeight: "bold",
              wordBreak: "break-word",
              display: "-webkit-box",
              WebkitBoxOrient: "vertical",
              WebkitLineClamp: 2,
              overflow: "hidden",
              lineHeight: 1.45,
            }}
          >
            {title}
          </Typography>
        </Box>
        <Box sx={{ minHeight: 28, width: "100%", px: 0.5 }}>
          <BookTagChips
            tags={book.tags}
            maxVisible={3}
            justifyContent="flex-start"
            onTagClick={onTagClick ? handleTagClick : undefined}
          />
        </Box>
      </CardActionArea>
    </Card>
  );
}
