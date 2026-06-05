import { useState } from "react";

import BookSearchApi from "../libs/apis/bookSearch";
import { toError } from "../libs/utils/error";
import { BookSearchResult } from "../types/bookSearch";

const bookSearchApi = new BookSearchApi();

export default function useBookMasterIsbnSearch() {
  const [results, setResults] = useState<BookSearchResult[]>([]);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [isSearching, setIsSearching] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const searchByIsbn = async (isbn13: string) => {
    setIsSearching(true);
    try {
      setError(null);
      const res = await bookSearchApi.search(isbn13);
      setResults(res.data.books);
      setIsDialogOpen(true);
    } catch (e: unknown) {
      setError(toError(e));
    } finally {
      setIsSearching(false);
    }
  };

  const closeDialog = () => {
    setIsDialogOpen(false);
  };

  return {
    results,
    isDialogOpen,
    isSearching,
    error,
    searchByIsbn,
    closeDialog,
  };
}
