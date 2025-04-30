import { useState } from "react";

import { CircularProgress, Typography } from "@mui/material";

import useSpecificUserBookReviews from "../../hooks/UseSpecificUserBookReviews";
import BookCards from "../parts/BookCards";
import ErrorAlert from "../parts/ErrorAlert";
import BookReviewDialog from "../parts/dialogs/BookReviewDialog";
import { BookWithReviews } from "../../types/data";
import BookCardsDisplayOptions from "../parts/BookCardsDisplayOptions";

type DialogState = {
  open: boolean;
  book?: BookWithReviews;
};

const initialState: DialogState = {
  open: false,
  book: undefined,
};

type LatestBookReviewsContainerProps = {
  userId: string;
};

export default function SpecificUserBookReviewsContainer(
  props: LatestBookReviewsContainerProps
) {
  const { userId } = props;
  const [dialogState, setDialogState] = useState<DialogState>(initialState);
  const { filteredReviews, displayOption, setDisplayOption, userName, error, loading } =
    useSpecificUserBookReviews(userId);

  const handleClosed = () => {
    setDialogState(initialState);
  };

  if (loading) {
    return <CircularProgress />;
  }
  if (error) {
    return <ErrorAlert error={error} />;
  }
  return (
    <>
      <Typography variant="h6" align="center" gutterBottom>
        {userName}さんの本棚
      </Typography>
      <BookCardsDisplayOptions option={displayOption} onChange={setDisplayOption} />
      <BookCards
        books={filteredReviews}
        isRibbonRender={true}
        onSelect={(b) => {
          if (!b) return;
          setDialogState({ open: true, book: b });
        }}
      ></BookCards>
      <BookReviewDialog {...dialogState} onClose={handleClosed} />
    </>
  );
}
