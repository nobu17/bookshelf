import { useEffect, useState } from "react";
import {
  Button,
  CircularProgress,
  Stack,
  TextField,
  Tooltip,
} from "@mui/material";
import SearchIcon from "@mui/icons-material/Search";

import BooksApi from "../../libs/apis/books";
import useAuthApi from "../../hooks/UseAuthApi";
import { BookMasterInfo } from "../../types/data";
import ErrorAlert from "../parts/ErrorAlert";
import BookMasterDataGrid from "../parts/BookMasterDataGrid";
import useBookMasterEditDialog from "../../hooks/dialogs/UseBookMasterEditDialog";

const bookApi = new BooksApi();

export default function BookMastersContainer() {
  useAuthApi(bookApi);
  const [keyword, setKeyword] = useState("");
  const [books, setBooks] = useState<BookMasterInfo[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const {
    openBookMasterEditDialog,
    isBookMasterEditLoading,
    renderBookMasterEditDialog,
  } = useBookMasterEditDialog({
    onUpdated: async () => {
      await loadAsync(keyword);
    },
  });

  useEffect(() => {
    loadAsync("");
  }, []);

  const loadAsync = async (searchKeyword: string) => {
    setLoading(true);
    try {
      const res = await bookApi.searchMasters(searchKeyword);
      setBooks(res.data.books);
      setError(null);
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

  const handleSearch = async () => {
    await loadAsync(keyword);
  };
  const handleEdit = (book: BookMasterInfo) => {
    openBookMasterEditDialog(book);
  };

  if (error) {
    return <ErrorAlert error={error} />;
  }

  return (
    <>
      <Stack direction={{ xs: "column", sm: "row" }} spacing={2} sx={{ mb: 2 }}>
        <TextField
          label="キーワード"
          value={keyword}
          onChange={(event) => setKeyword(event.target.value)}
          fullWidth
        />
        <Tooltip title="検索">
          <Button
            aria-label="search"
            variant="contained"
            onClick={handleSearch}
            sx={{
              minWidth: 56,
              px: 2,
            }}
          >
            <SearchIcon />
          </Button>
        </Tooltip>
      </Stack>
      {loading || isBookMasterEditLoading ? (
        <CircularProgress />
      ) : (
        <BookMasterDataGrid books={books} onEdit={handleEdit} />
      )}
      {renderBookMasterEditDialog()}
    </>
  );
}
