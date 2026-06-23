import {
  Dialog,
  DialogTitle,
  DialogContent,
  Box,
  Typography,
  Stack,
  Card,
  CardContent,
  IconButton,
  Tooltip,
  Divider,
  Chip,
  LinearProgress,
} from "@mui/material";
import Grid from "@mui/material/Grid2";
import EditIcon from "@mui/icons-material/Edit";
import CloseIcon from "@mui/icons-material/Close";
import { useEffect, useState } from "react";

import { BookWithReviews, Review, toJapanese } from "../../../types/data";
import { getBookInfoImageUrl, getFallbackImageUrl } from "../../../libs/utils/image";
import { dateToString } from "../../../libs/utils/date";
import LineBreakText from "../LineBreakText";
import BookTagChips from "../BookTagChips";
import GoogleBooksAttribution from "../GoogleBooksAttribution";
import BookSearchApi from "../../../libs/apis/bookSearch";

export type BookReviewDialogProps = {
  open: boolean;
  book?: BookWithReviews;
  onClose: () => void;
  onBookEdit?: () => void;
  isBookEditEnabled?: boolean;
};

export default function BookReviewDialog(props: BookReviewDialogProps) {
  const { onClose, open, book, onBookEdit, isBookEditEnabled } = props;
  const [description, setDescription] = useState<string | null>(null);
  const [isDescriptionLoading, setIsDescriptionLoading] = useState(false);

  const handleClose = () => {
    onClose();
  };
  const handleBookEdit = () => {
    if (!onBookEdit) {
      return;
    }
    onBookEdit();
  };

  useEffect(() => {
    if (!open || !book?.isbn13) {
      setDescription(null);
      setIsDescriptionLoading(false);
      return;
    }

    let isActive = true;
    setDescription(null);
    setIsDescriptionLoading(true);
    new BookSearchApi()
      .findDescriptionByIsbn13(book.isbn13)
      .then((result) => {
        if (!isActive) return;
        setDescription(result.data.description);
      })
      .catch(() => {
        if (!isActive) return;
        setDescription(null);
      })
      .finally(() => {
        if (!isActive) return;
        setIsDescriptionLoading(false);
      });

    return () => {
      isActive = false;
    };
  }, [open, book?.isbn13]);

  if (!book) {
    return <></>;
  }

  return (
    <Dialog
      scroll="paper"
      fullWidth
      maxWidth="lg"
      onClose={handleClose}
      open={open}
    >
      <DialogTitle
        sx={{
          pr: 6,
          textAlign: "left",
          fontWeight: "bold",
          lineHeight: 1.35,
        }}
      >
        <Typography variant="h6" component="div" sx={{ fontWeight: "bold" }}>
          {book.title}
        </Typography>
        <Tooltip title="閉じる">
          <IconButton
            aria-label="close"
            color="error"
            onClick={handleClose}
            size="small"
            sx={{ position: "absolute", right: 8, top: 8 }}
          >
            <CloseIcon />
          </IconButton>
        </Tooltip>
        {isBookEditEnabled ? (
          <Tooltip title="書籍マスタ編集">
            <IconButton
              aria-label="book-edit"
              color="primary"
              onClick={handleBookEdit}
              size="small"
              sx={{ position: "absolute", right: 44, top: 8 }}
            >
              <EditIcon />
            </IconButton>
          </Tooltip>
        ) : (
          <></>
        )}
      </DialogTitle>
      <DialogContent dividers sx={{ px: { xs: 2, md: 3 }, py: 3 }}>
        <Grid container spacing={{ xs: 3, md: 4 }}>
          <Grid size={{ xs: 12, md: 4 }}>
            <Stack
              spacing={2}
              sx={{
                position: { md: "sticky" },
                top: { md: 16 },
                alignItems: "center",
                textAlign: "left",
              }}
            >
              <Box sx={{ textAlign: "center", width: "100%" }}>
                <Box
                  component="img"
                  sx={{
                    maxHeight: { xs: 220, md: 280 },
                    width: "100%",
                    objectFit: "contain",
                    filter: "drop-shadow(0 6px 12px rgba(0, 0, 0, 0.16))",
                  }}
                  src={getBookInfoImageUrl(book)}
                  onError={(e) => {
                    e.currentTarget.src = getFallbackImageUrl();
                  }}
                />
                <GoogleBooksAttribution imageUrl={book.imageUrl} />
              </Box>
              <Box sx={{ width: "100%" }}>
                <Typography variant="subtitle2" color="text.secondary">
                  出版社
                </Typography>
                <Typography sx={{ mb: 1.5 }}>{book.publisher}</Typography>
                <Typography variant="subtitle2" color="text.secondary">
                  著者
                </Typography>
                <Typography sx={{ mb: 1.5 }}>
                  {book.authors.join(", ")}
                </Typography>
                <Typography variant="subtitle2" color="text.secondary">
                  出版日
                </Typography>
                <Typography sx={{ mb: 1.5 }}>
                  {dateToString(book.publishedAt)}
                </Typography>
                <Divider sx={{ my: 2 }} />
                <BookTagChips tags={book.tags} />
              </Box>
            </Stack>
          </Grid>
          <Grid size={{ xs: 12, md: 8 }}>
            <Stack spacing={2}>
              {isDescriptionLoading || description ? (
                <Card
                  variant="outlined"
                  sx={{
                    borderColor: "rgba(31, 41, 55, 0.14)",
                    borderRadius: "8px",
                  }}
                >
                  <CardContent sx={{ p: { xs: 2, md: 2.5 } }}>
                    <Typography variant="h6" component="h2" fontWeight="bold" sx={{ mb: 1 }}>
                      概要
                    </Typography>
                    {isDescriptionLoading ? (
                      <LinearProgress />
                    ) : (
                      <Typography
                        color="text.secondary"
                        sx={{ lineHeight: 1.85, whiteSpace: "pre-line" }}
                      >
                        {description}
                      </Typography>
                    )}
                  </CardContent>
                </Card>
              ) : (
                <></>
              )}
              <Stack
                direction="row"
                alignItems="center"
                justifyContent="space-between"
                spacing={2}
              >
                <Typography variant="h6" component="h2" fontWeight="bold">
                  レビュー
                </Typography>
                <Chip label={`${book.reviews.length}件`} size="small" />
              </Stack>
              {book.reviews.length === 0 ? (
                <Typography color="text.secondary">
                  レビューはまだありません。
                </Typography>
              ) : (
                book.reviews.map((r) => ReviewCard(r))
              )}
            </Stack>
          </Grid>
        </Grid>
      </DialogContent>
    </Dialog>
  );
}

function ReviewCard(review: Review) {
  return (
    <Card
      variant="outlined"
      sx={{
        borderColor: "rgba(31, 41, 55, 0.14)",
        borderRadius: "8px",
        boxShadow: "0 1px 2px rgba(0, 0, 0, 0.03)",
      }}
      key={review.reviewId}
    >
      <CardContent sx={{ p: { xs: 2, md: 2.5 } }}>
        <Stack
          direction={{ xs: "column", sm: "row" }}
          spacing={1}
          alignItems={{ xs: "flex-start", sm: "center" }}
          justifyContent="space-between"
          sx={{ mb: 1.5 }}
        >
          <Typography fontWeight="bold">{review.user.name}</Typography>
          <Stack direction="row" spacing={1} alignItems="center">
            <Chip label={toJapanese(review.state)} color="primary" size="small" />
            {review.completedAt ? (
              <Typography variant="body2" color="text.secondary">
                {dateToString(review.completedAt)}
              </Typography>
            ) : (
              <></>
            )}
          </Stack>
        </Stack>
        <Divider sx={{ mb: 2 }} />
        {review.content ? (
          <Typography
            variant="body1"
            sx={{ lineHeight: 1.85, whiteSpace: "normal" }}
          >
            <LineBreakText text={review.content} />
          </Typography>
        ) : (
          <Typography color="text.secondary">感想は未入力です。</Typography>
        )}
      </CardContent>
    </Card>
  );
}
