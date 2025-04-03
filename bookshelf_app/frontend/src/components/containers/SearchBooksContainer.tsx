import { Button, CircularProgress, Typography } from "@mui/material";

import useSearchBooks from "../../hooks/UseSearchBooks";
import BookSearchCards from "../parts/BookSearchCards";
import ErrorAlert from "../parts/ErrorAlert";
import { NdlBook, NdlBookWithReviews } from "../../types/ndls";
import BookSearchInput from "../parts/BookSearchInput";
import { useState } from "react";
import { ReviewStateDef } from "../../types/data";
import { ReviewEditInfo } from "../parts/BookReviewEditForm";
import OneBookReviewsListDialogContainer from "./OneBookReviewsListDialogContainer";
import BookReviewCreateFormDialogContainers from "./BookReviewCreateFormDialogContainers";
import ISBN13CaptureDialog from "../parts/dialogs/ISBN13CaptureDialog";

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
  const [word, setWord] = useState("");
  const [isEditOpen, setIsEditOpen] = useState(false);
  const [isReviewListOpen, setIsReviewListOpen] = useState(false);
  const [bookId, setBookId] = useState("");
  const [createItem, setCreateItem] = useState<ReviewEditInfo | null>(null);
  const [selectBook, setSelectBook] = useState<NdlBook | null>(null);

  const [isCaptureOpen, setIsCaptureOpen] = useState(false);

  const handleSelect = (book: NdlBookWithReviews) => {
    // no existing review case, show create new dialog
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
    setCreateItem(null);
    setSelectBook(null);
    if (!item || !selectBook) {
      return;
    }
    await reload(word);
  };

  const handleSubmit = async (submitWord: string) => {
    setWord(submitWord);
    await search(submitWord);
  };

  const handleCaptureStart = () => {
    setIsCaptureOpen(true);
  };

  const handleCaptureClose = async (isbn13: string | null) => {
    setIsCaptureOpen(false);
    if (isbn13) {
      setWord(isbn13);
      await search(isbn13);
    }
  };

  return (
    <>
      {displayError(error)}
      <BookSearchInput
        word={word}
        onSubmit={handleSubmit}
        isLoading={loading}
        key={word}
      ></BookSearchInput>
      <Button variant="outlined" onClick={handleCaptureStart}>
        バーコードから探す
      </Button>
      <br />
      {loading ? <CircularProgress /> : displayResult(books, handleSelect)}
      <BookReviewCreateFormDialogContainers
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
      <ISBN13CaptureDialog open={isCaptureOpen} onClose={handleCaptureClose} />
    </>
  );
}
