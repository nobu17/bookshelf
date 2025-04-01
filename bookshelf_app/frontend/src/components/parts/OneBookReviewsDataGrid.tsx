import { Box, Button, Container, Stack, Typography } from "@mui/material";
import { GenericBookInfoWithReviews, Review } from "../../types/data";
import ReviewsDataGrid from "./ReviewsDataGrid";
import { dateToString } from "../../libs/utils/date";
import { getFallbackImageUrl, getImageUrl } from "../../libs/utils/image";

type OneBookReviewsDataGridProps = {
  bookWithReviews: GenericBookInfoWithReviews;
  onEdit?: (review: Review) => void;
  onDelete?: (review: Review) => void;
  onAdd?: () => void;
};

export default function OneBookReviewsDataGrid(
  props: OneBookReviewsDataGridProps
) {
  const { bookWithReviews, onEdit, onDelete, onAdd } = props;

  return (
    <>
      <Container maxWidth="sm" sx={{ py: 1 }}>
        <Stack spacing={3}>
          <Typography variant="subtitle1" align="left">
            書籍名：{bookWithReviews.title}
            <br />
            出版社：{bookWithReviews.publisher}
            <br />
            著者：{bookWithReviews.authors.join(": ")}
            <br />
            出版年：{dateToString(bookWithReviews.publishedAt)}
          </Typography>
          <Box
            component="img"
            sx={{ height: "150px", width: "auto", objectFit: "contain" }}
            src={getImageUrl(bookWithReviews.isbn13)}
            onError={(e) => {
              e.currentTarget.src = getFallbackImageUrl();
            }}
          />
          <Button variant="contained" onClick={onAdd}>
            新規投稿
          </Button>
        </Stack>
      </Container>
      <ReviewsDataGrid
        reviews={bookWithReviews.reviews}
        onDelete={onDelete}
        onEdit={onEdit}
      />
    </>
  );
}
