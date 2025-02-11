import { CircularProgress } from "@mui/material";

import useLatestBookReviews from "../../hooks/dialogs/UseLatestBookReviews";
import BookCards from "../parts/BookCards";
import ErrorAlert from "../parts/ErrorAlert";

export default function LatestBookReviewsContainer() {
  const { bookWithReviews, error, loading } = useLatestBookReviews();
  if (loading) {
    return <CircularProgress />;
  }
  if (error) {
    return <ErrorAlert error={error}/>;
  }
  return (
    <BookCards
      books={bookWithReviews}
      onSelect={(b) => {
        console.log(b);
      }}
    ></BookCards>
  );
}
