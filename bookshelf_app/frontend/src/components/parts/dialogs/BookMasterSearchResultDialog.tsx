import {
  Card,
  CardActionArea,
  CardContent,
  CardMedia,
  Dialog,
  DialogContent,
  DialogTitle,
  Stack,
  Typography,
  Box,
} from "@mui/material";

import { dateToString } from "../../../libs/utils/date";
import { getFallbackImageUrl } from "../../../libs/utils/image";
import { BookSearchResult } from "../../../types/bookSearch";
import GoogleBooksAttribution from "../GoogleBooksAttribution";

type BookMasterSearchResultDialogProps = {
  open: boolean;
  books: BookSearchResult[];
  onSelect: (book: BookSearchResult) => void;
  onClose: () => void;
};

export default function BookMasterSearchResultDialog(
  props: BookMasterSearchResultDialogProps
) {
  const { open, books, onSelect, onClose } = props;

  return (
    <Dialog open={open} onClose={onClose} fullWidth maxWidth="md">
      <DialogTitle>検索結果</DialogTitle>
      <DialogContent>
        <Stack spacing={2}>
          {books.length === 0 ? (
            <Typography>候補が見つかりませんでした。</Typography>
          ) : (
            books.map((book) => (
              <Card key={`${book.source}:${book.sourceId}`}>
                <CardActionArea onClick={() => onSelect(book)}>
                  <Stack direction={{ xs: "column", sm: "row" }} spacing={2}>
                    <Box
                      sx={{
                        width: { xs: "100%", sm: 120 },
                        textAlign: "center",
                        flexShrink: 0,
                      }}
                    >
                      <CardMedia
                        component="img"
                        sx={{
                          width: "100%",
                          height: 168,
                          objectFit: "contain",
                          p: 1,
                        }}
                        image={book.imageUrl || getFallbackImageUrl()}
                        onError={(e) => {
                          e.currentTarget.src = getFallbackImageUrl();
                        }}
                      />
                      <GoogleBooksAttribution imageUrl={book.imageUrl} compact />
                    </Box>
                    <CardContent>
                      <Typography fontWeight="bold">{book.title}</Typography>
                      <Typography>ISBN13: {book.isbn13}</Typography>
                      <Typography>出版社: {book.publisher}</Typography>
                      <Typography>著者: {book.authors.join(", ")}</Typography>
                      <Typography>
                        出版日: {dateToString(book.publishedAt)}
                      </Typography>
                      {book.description ? (
                        <Typography
                          color="text.secondary"
                          sx={{
                            mt: 1.5,
                            whiteSpace: "pre-line",
                            display: "-webkit-box",
                            WebkitBoxOrient: "vertical",
                            WebkitLineClamp: 4,
                            overflow: "hidden",
                            lineHeight: 1.7,
                          }}
                        >
                          {book.description}
                        </Typography>
                      ) : (
                        <></>
                      )}
                    </CardContent>
                  </Stack>
                </CardActionArea>
              </Card>
            ))
          )}
        </Stack>
      </DialogContent>
    </Dialog>
  );
}
