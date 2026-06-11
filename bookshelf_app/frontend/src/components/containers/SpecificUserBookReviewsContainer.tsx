import { useState } from "react";

import { CircularProgress, Typography } from "@mui/material";

import useSpecificUserBookReviews from "../../hooks/UseSpecificUserBookReviews";
import BookCards from "../parts/BookCards";
import ErrorAlert from "../parts/ErrorAlert";
import BookReviewDialog from "../parts/dialogs/BookReviewDialog";
import { BookTag, BookWithReviews } from "../../types/data";
import BookCardsDisplayOptions from "../parts/BookCardsDisplayOptions";
import { useAuth } from "../contexts/AuthContext";
import useBookMasterEditDialog from "../../hooks/dialogs/UseBookMasterEditDialog";
import { canEditBookMaster } from "../../libs/utils/permissions";
import SelectedTagFilterBar from "../parts/SelectedTagFilterBar";
import { filterBooksByTag } from "../../libs/utils/bookTags";

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
  const [selectedTag, setSelectedTag] = useState<BookTag | null>(null);
  const { filteredReviews, displayOption, setDisplayOption, userName, error, loading, loadAsync } =
    useSpecificUserBookReviews(userId);
  const {
    state,
  } = useAuth();
  const { openBookMasterEditDialog, renderBookMasterEditDialog } =
    useBookMasterEditDialog({
      onUpdated: async () => {
        await loadAsync(userId);
      },
    });

  const handleClosed = () => {
    setDialogState(initialState);
  };
  const handleBookEdit = () => {
    openBookMasterEditDialog(dialogState.book);
  };
  const handleTagClick = (tag: BookTag) => {
    setSelectedTag((current) => (current?.id === tag.id ? null : tag));
  };
  const displayedBooks = filterBooksByTag(filteredReviews, selectedTag);

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
      <SelectedTagFilterBar
        tag={selectedTag}
        resultCount={displayedBooks.length}
        onClear={() => setSelectedTag(null)}
      />
      {selectedTag && displayedBooks.length === 0 ? (
        <Typography align="center" color="text.secondary" sx={{ my: 4 }}>
          選択中のタグに一致する本はありません。
        </Typography>
      ) : (
        <></>
      )}
      <BookCards
        books={displayedBooks}
        isRibbonRender={true}
        onTagClick={handleTagClick}
        onSelect={(b) => {
          if (!b) return;
          setDialogState({ open: true, book: b });
        }}
      ></BookCards>
      <BookReviewDialog
        {...dialogState}
        onClose={handleClosed}
        onBookEdit={handleBookEdit}
        isBookEditEnabled={canEditBookMaster(state)}
      />
      {renderBookMasterEditDialog()}
    </>
  );
}
