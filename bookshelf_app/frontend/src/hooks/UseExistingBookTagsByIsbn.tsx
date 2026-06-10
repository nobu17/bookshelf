import { useEffect, useState } from "react";

import BooksApi from "../libs/apis/books";
import { ApiError } from "../libs/apis/apibase";
import { BookTag } from "../types/data";
import { toError } from "../libs/utils/error";
import useAuthApi from "./UseAuthApi";

const booksApi = new BooksApi();

export default function useExistingBookTagsByIsbn(
  isbn13: string | null,
  enabled: boolean
) {
  useAuthApi(booksApi);
  const [tags, setTags] = useState<BookTag[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    if (!enabled || !isbn13) {
      setTags([]);
      setError(null);
      return;
    }

    let isActive = true;
    const load = async () => {
      setLoading(true);
      setError(null);
      try {
        const res = await booksApi.findByIsbn13(isbn13);
        if (!isActive) {
          return;
        }
        setTags(res.data.books[0]?.tags ?? []);
      } catch (e: unknown) {
        if (!isActive) {
          return;
        }
        if (e instanceof ApiError && e.isNotFound()) {
          setTags([]);
          return;
        }
        setTags([]);
        setError(toError(e));
      } finally {
        if (isActive) {
          setLoading(false);
        }
      }
    };

    void load();

    return () => {
      isActive = false;
    };
  }, [enabled, isbn13]);

  return {
    tags,
    loading,
    error,
  };
}
