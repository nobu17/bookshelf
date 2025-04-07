import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Box,
  Typography,
  Stack,
  Card,
  CardContent,
} from "@mui/material";
import Grid from "@mui/material/Grid2";

import { BookWithReviews, Review, toJapanese } from "../../../types/data";
import { getFallbackImageUrl, getImageUrl } from "../../../libs/utils/image";
import { dateToString } from "../../../libs/utils/date";
import LineBreakText from "../LineBreakText";

export type BookReviewDialogProps = {
  open: boolean;
  book?: BookWithReviews;
  onClose: () => void;
};

export default function BookReviewDialog(props: BookReviewDialogProps) {
  const { onClose, open, book } = props;

  const handleClose = () => {
    onClose();
  };

  if (!book) {
    return <></>;
  }

  return (
    <Dialog
      scroll="paper"
      fullWidth
      maxWidth="md"
      onClose={handleClose}
      open={open}
    >
      <DialogTitle textAlign="center">{book.title}</DialogTitle>
      <DialogContent>
        <Stack
          alignItems={{ xs: "center", md: "stretch" }}
          justifyContent={{ xs: "center", md: "center" }}
          direction={{ xs: "column", md: "row" }}
          spacing={{ xs: 1, sm: 2, md: 4 }}
        >
          <img
            height="200"
            style={{ padding: "1em 0em 0em 0em", objectFit: "contain" }}
            src={getImageUrl(book.isbn13)}
            onError={(e) => {
              e.currentTarget.src = getFallbackImageUrl();
            }}
          />
          <Grid
            container
            spacing={1}
            sx={{
              justifyContent: "center",
              alignItems: "stretch",
              bgcolor: "",
            }}
          >
            <Grid>
              <Box sx={{ bgcolor: "", m: 2 }}>
                <Typography>出版社: {book.publisher}</Typography>
                <Typography>著者: {book.authors.join(",")}</Typography>
                <Typography sx={{ mb: 1 }}>
                  出版日: {dateToString(book.publishedAt)}
                </Typography>
                {book.reviews.map((r) => {
                  return ReviewCard(r);
                })}
              </Box>
            </Grid>
          </Grid>
        </Stack>
      </DialogContent>
      <DialogActions>
        <Box>
          <Button onClick={handleClose}>OK</Button>
        </Box>
      </DialogActions>
    </Dialog>
  );
}

function ReviewCard(review: Review) {
  return (
    <Card sx={{ minWidth: 275, border: 1, m: 1 }} key={review.reviewId}>
      <CardContent>
        <Typography gutterBottom sx={{ fontSize: 14 }}>
          {review.user.name}
        </Typography>
        <Typography
          gutterBottom
          sx={{ fontSize: 14, color: "blue", borderBottom: 1 }}
        >
          {toJapanese(review.state) +
            (review.completedAt ? " :" + dateToString(review.completedAt) : "")}
        </Typography>
        {review.content ? (
          <Typography variant="body2">
            <LineBreakText text={review.content} />
          </Typography>
        ) : (
          <></>
        )}
      </CardContent>
    </Card>
  );
}
