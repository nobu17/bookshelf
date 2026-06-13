import { useState } from "react";

import { CircularProgress, Typography } from "@mui/material";

import useLatestBookReviews from "../../hooks/UseLatestBookReviews";
import BookCards from "../parts/BookCards";
import ErrorAlert from "../parts/ErrorAlert";
import BookReviewDialog from "../parts/dialogs/BookReviewDialog";
import { BookTag, BookWithReviews } from "../../types/data";
import { useAuth } from "../contexts/AuthContext";
import useBookMasterEditDialog from "../../hooks/dialogs/UseBookMasterEditDialog";
import { canEditBookMaster } from "../../libs/utils/permissions";
import SelectedTagFilterBar from "../parts/SelectedTagFilterBar";
import {
  filterBooksByKeyword,
  filterBooksByTag,
} from "../../libs/utils/bookTags";
import BookListSearchInput from "../parts/BookListSearchInput";

type DialogState = {
  open: boolean;
  book?: BookWithReviews;
};

const initialState: DialogState = {
  open: false,
  book: undefined,
};

export default function LatestBookReviewsContainer() {
  const [dialogState, setDialogState] = useState<DialogState>(initialState);
  const [selectedTag, setSelectedTag] = useState<BookTag | null>(null);
  const [searchKeyword, setSearchKeyword] = useState("");
  const { bookWithReviews, error, loading, loadAsync } = useLatestBookReviews();
  const {
    state,
  } = useAuth();
  const { openBookMasterEditDialog, renderBookMasterEditDialog } =
    useBookMasterEditDialog({
      onUpdated: async () => {
        await loadAsync();
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
  const searchedBooks = filterBooksByKeyword(bookWithReviews, searchKeyword);
  const filteredBooks = filterBooksByTag(searchedBooks, selectedTag);
  const isFiltered = searchKeyword.trim() !== "" || selectedTag !== null;

  if (loading) {
    return <CircularProgress />;
  }
  if (error) {
    return <ErrorAlert error={error} />;
  }
  return (
    <>
      <BookListSearchInput
        value={searchKeyword}
        onChange={setSearchKeyword}
      />
      <SelectedTagFilterBar
        tag={selectedTag}
        resultCount={filteredBooks.length}
        onClear={() => setSelectedTag(null)}
      />
      {isFiltered && filteredBooks.length === 0 ? (
        <Typography align="center" color="text.secondary" sx={{ my: 4 }}>
          検索条件に一致する本はありません。
        </Typography>
      ) : (
        <></>
      )}
      <BookCards
        books={filteredBooks}
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
