import { useState } from "react";
import { Snackbar } from "@mui/material";

import BooksApi from "../../libs/apis/books";
import useAuthApi from "../UseAuthApi";
import { BookInfo } from "../../types/data";
import BookMasterEditFormDialog from "../../components/parts/dialogs/BookMasterEditFormDialog";
import {
  BookMasterEditInfo,
  toBookUpdateParameter,
} from "../../components/parts/BookMasterEditForm";

type UseBookMasterEditDialogOptions = {
  onUpdated?: (book: BookInfo) => Promise<void> | void;
};

const bookApi = new BooksApi();

export default function useBookMasterEditDialog(
  options: UseBookMasterEditDialogOptions = {}
) {
  const { onUpdated } = options;
  useAuthApi(bookApi);
  const [editBook, setEditBook] = useState<BookInfo | null>(null);
  const [error, setError] = useState<Error | null>(null);
  const [loading, setLoading] = useState(false);

  const open = (book: BookInfo | null | undefined) => {
    if (!book) {
      return;
    }
    setError(null);
    setEditBook(book);
  };

  const handleClose = async (item: BookMasterEditInfo | null) => {
    if (!item || !editBook) {
      setEditBook(null);
      return;
    }
    setLoading(true);
    try {
      const updated = await bookApi.update(
        editBook.bookId,
        toBookUpdateParameter(item)
      );
      await onUpdated?.(updated.data);
      setError(null);
      setEditBook(null);
    } catch (e: unknown) {
      if (e instanceof Error) {
        setError(e);
        return;
      }
      setError(new Error("unexpected error."));
    } finally {
      setLoading(false);
    }
  };

  const renderBookMasterEditDialog = () => (
    <>
      <BookMasterEditFormDialog
        open={editBook !== null}
        bookInfo={editBook}
        onClose={handleClose}
      />
      <Snackbar
        anchorOrigin={{ vertical: "top", horizontal: "center" }}
        open={error ? true : false}
        autoHideDuration={6000}
        message={error ? error.message : ""}
      />
    </>
  );

  return {
    openBookMasterEditDialog: open,
    isBookMasterEditLoading: loading,
    bookMasterEditError: error,
    renderBookMasterEditDialog,
  };
}
