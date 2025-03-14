import { CircularProgress, Typography } from "@mui/material";

import useSearchBooks from "../../hooks/UseSearchBooks";
import BookSearchCards from "../parts/BookSearchCards";
import ErrorAlert from "../parts/ErrorAlert";
import { NdlBook, NdlBookWithReviews } from "../../types/ndls";
import BookSearchInput from "../parts/BookSearchInput";
import BookReviewCreateFormDialog from "../parts/dialogs/BookReviewCreateFormDialog";
import { useEffect, useState } from "react";
import { ReviewStateDef } from "../../types/data";
import { ReviewEditInfo } from "../parts/BookReviewEditForm";
import useBookAndReviewCreate from "../../hooks/UseBookAndReviewCreate";
import { useGlobalSpinnerContext } from "../contexts/GlobalSpinnerContext";
import { useMessageDialog } from "../../hooks/dialogs/UseMessageDialog";
import OneBookReviewsListDialogContainer from "./OneBookReviewsListDialogContainer";

const displayError = (error: Error | undefined) => {
  if (error) {
    return <ErrorAlert error={error} />;
  }
};

const displayResult = (
  books: NdlBookWithReviews[],
  handleSelect: (book: NdlBookWithReviews) => void
) => {
  if (!books || books.length === 0) {
    return <Typography variant="subtitle1">検索結果: 0 件</Typography>;
  }
  return (
    <>
      <Typography variant="subtitle1">検索結果: {books.length} 件</Typography>
      <BookSearchCards
        books={books}
        onSelect={(b) => {
          handleSelect(b);
        }}
      ></BookSearchCards>
    </>
  );
};

export default function SearchBooksContainer() {
  const { loading, error, books, search, reload } = useSearchBooks();
  const {
    loading: bookLoading,
    error: bookError,
    create,
  } = useBookAndReviewCreate();
  const { setIsSpinnerOn } = useGlobalSpinnerContext();
  const { renderDialog, showMessageDialog } = useMessageDialog();
  const [word, setWord] = useState("");
  const [isEditOpen, setIsEditOpen] = useState(false);
  const [isReviewListOpen, setIsReviewListOpen] = useState(false);
  const [bookId, setBookId] = useState("");
  const [createItem, setCreateItem] = useState<ReviewEditInfo | null>(null);
  const [selectBook, setSelectBook] = useState<NdlBook | null>(null);

  useEffect(() => {
    setIsSpinnerOn(bookLoading);
  }, [setIsSpinnerOn, bookLoading]);

  const handleSelect = (book: NdlBookWithReviews) => {
    if (book.reviews.length === 0) {
      setSelectBook(book);
      const initial = {
        content: "",
        isDraft: false,
        state: ReviewStateDef.Completed,
        completedAt: new Date(),
      };
      setCreateItem(initial);
      setIsEditOpen(true);
      return;
    }
    if (!book.bookId) {
      return;
    }
    // if review exists, display review list dialog
    setIsReviewListOpen(true);
    setBookId(book.bookId);
  };

  const handleReviewListClose = () => {
    setIsReviewListOpen(false);
    setBookId("");
  };

  const handleCreateClose = async (item: ReviewEditInfo | null) => {
    setIsEditOpen(false);
    if (!item || !selectBook) {
      return;
    }
    await create(selectBook, item);
    setCreateItem(null);
    setSelectBook(null);
    await showMessageDialog("情報", "レビュー投稿完了しました。");
    await reload(word);
  };

  const handleSubmit = async (submitWord: string) => {
    setWord(submitWord);
    await search(submitWord);
  };

  return (
    <>
      {displayError(error)}
      {displayError(bookError)}
      <BookSearchInput
        word={word}
        onSubmit={handleSubmit}
        isLoading={loading}
      ></BookSearchInput>
      {loading ? <CircularProgress /> : displayResult(books, handleSelect)}
      <BookReviewCreateFormDialog
        open={isEditOpen}
        editItem={createItem}
        bookInfo={selectBook}
        onClose={handleCreateClose}
      />
      <OneBookReviewsListDialogContainer
        open={isReviewListOpen}
        bookId={bookId}
        onClose={handleReviewListClose}
      />
      {renderDialog()}
    </>
  );
}
