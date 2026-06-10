import { useEffect, useState } from "react";

import TagsApi from "../libs/apis/tags";
import useAuthApi from "./UseAuthApi";
import { BookTag } from "../types/data";
import { toError } from "../libs/utils/error";

const tagsApi = new TagsApi();

export default function useBookTags() {
  useAuthApi(tagsApi);
  const [tags, setTags] = useState<BookTag[]>([]);
  const [error, setError] = useState<Error | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadAsync();
  }, []);

  const loadAsync = async () => {
    setLoading(true);
    try {
      setError(null);
      const res = await tagsApi.list();
      setTags(res.data.tags);
    } catch (e: unknown) {
      setError(toError(e));
    } finally {
      setLoading(false);
    }
  };

  return {
    tags,
    error,
    loading,
    reloadTags: loadAsync,
  };
}
