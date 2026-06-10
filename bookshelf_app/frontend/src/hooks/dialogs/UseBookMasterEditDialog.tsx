import { useState } from "react";
import { Snackbar } from "@mui/material";

import BooksApi from "../../libs/apis/books";
import TagsApi from "../../libs/apis/tags";
import useAuthApi from "../UseAuthApi";
import { BookInfo } from "../../types/data";
import BookMasterEditFormDialog from "../../components/parts/dialogs/BookMasterEditFormDialog";
import {
  BookMasterEditInfo,
  toBookUpdateParameter,
} from "../../libs/services/bookMasterEdit";
import { updateBookTagsByNames } from "../../libs/services/bookTags";
import { toError } from "../../libs/utils/error";

type UseBookMasterEditDialogOptions = {
  onUpdated?: (book: BookInfo) => Promise<void> | void;
};

const bookApi = new BooksApi();
const tagsApi = new TagsApi();

export default function useBookMasterEditDialog(
  options: UseBookMasterEditDialogOptions = {}
) {
  const { onUpdated } = options;
  useAuthApi(bookApi);
  useAuthApi(tagsApi);
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
      const tags = await updateBookTagsByNames(
        bookApi,
        tagsApi,
        editBook.bookId,
        item.tagNames
      );
      await onUpdated?.({ ...updated.data, tags });
      setError(null);
      setEditBook(null);
    } catch (e: unknown) {
      setError(toError(e));
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
