import {
  Button,
  Card,
  CardActions,
  CardContent,
  CircularProgress,
  FormControl,
  InputAdornment,
  InputLabel,
  MenuItem,
  Pagination,
  Select,
  Stack,
  TextField,
  ToggleButton,
  ToggleButtonGroup,
  Typography,
} from "@mui/material";
import MenuBookIcon from "@mui/icons-material/MenuBook";
import SearchIcon from "@mui/icons-material/Search";

import useSearchBooks from "../../hooks/UseSearchBooks";
import BookSearchCards from "../parts/BookSearchCards";
import ErrorAlert from "../parts/ErrorAlert";
import {
  BookSearchResult,
  BookSearchResultWithReviews,
} from "../../types/bookSearch";
import BookSearchInput from "../parts/BookSearchInput";
import { useEffect, useState } from "react";
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
  books: BookSearchResultWithReviews[],
  handleSelect: (book: BookSearchResultWithReviews) => void,
  totalCount = books.length
) => {
  if (!books || books.length === 0) {
    return <Typography variant="subtitle1">検索結果: 0 件</Typography>;
  }
  return (
    <>
      <Typography variant="subtitle1">検索結果: {totalCount} 件</Typography>
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
  const {
    loading,
    error,
    books,
    publishers,
    search,
    searchPublisher,
    publisherPagination,
    reload,
  } = useSearchBooks();
  const [word, setWord] = useState("");
  const [publisherKeyword, setPublisherKeyword] = useState("");
  const [selectedPublisherId, setSelectedPublisherId] = useState("");
  const [searchMode, setSearchMode] = useState<"keyword" | "publisher">(
    "keyword"
  );
  const [isEditOpen, setIsEditOpen] = useState(false);
  const [isReviewListOpen, setIsReviewListOpen] = useState(false);
  const [bookId, setBookId] = useState("");
  const [createItem, setCreateItem] = useState<ReviewEditInfo | null>(null);
  const [selectBook, setSelectBook] = useState<BookSearchResult | null>(null);

  const [isCaptureOpen, setIsCaptureOpen] = useState(false);
  const selectedPublisher = publishers.find(
    (publisher) => publisher.publisherId === selectedPublisherId
  );

  useEffect(() => {
    if (!selectedPublisherId && publishers.length > 0) {
      setSelectedPublisherId(publishers[0].publisherId);
    }
  }, [publishers, selectedPublisherId]);

  const handleSelect = (book: BookSearchResultWithReviews) => {
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
    if (searchMode === "publisher") {
      if (!selectedPublisherId) {
        return;
      }
      await searchPublisher(
        selectedPublisherId,
        publisherKeyword,
        publisherPagination?.page ?? 1
      );
      return;
    }
    await reload(word);
  };

  const handleSubmit = async (submitWord: string) => {
    setSearchMode("keyword");
    setWord(submitWord);
    await search(submitWord);
  };

  const handlePublisherSearch = async () => {
    if (!selectedPublisherId) {
      return;
    }
    setSearchMode("publisher");
    await searchPublisher(selectedPublisherId, publisherKeyword, 1);
  };

  const handlePublisherPageChange = async (_: unknown, page: number) => {
    if (!selectedPublisherId) {
      return;
    }
    await searchPublisher(selectedPublisherId, publisherKeyword, page);
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
      <ToggleButtonGroup
        exclusive
        value={searchMode}
        onChange={(_, value) => {
          if (value) {
            setSearchMode(value);
          }
        }}
        sx={{ mx: 1, mt: 1, mb: 3 }}
      >
        <ToggleButton value="keyword" disabled={loading}>
          <SearchIcon fontSize="small" sx={{ mr: 1 }} />
          キーワード検索
        </ToggleButton>
        <ToggleButton value="publisher" disabled={loading}>
          <MenuBookIcon fontSize="small" sx={{ mr: 1 }} />
          出版社から探す
        </ToggleButton>
      </ToggleButtonGroup>
      {searchMode === "keyword" ? (
        <>
          <BookSearchInput
            word={word}
            onSubmit={handleSubmit}
            isLoading={loading}
            key={word}
          ></BookSearchInput>
          <Button variant="outlined" onClick={handleCaptureStart}>
            バーコードから探す
          </Button>
        </>
      ) : (
        <Stack
          spacing={2}
          sx={{
            mx: "auto",
            my: 1,
            px: 1,
            maxWidth: 640,
            width: "100%",
          }}
        >
          <Card variant="outlined" sx={{ borderRadius: 1 }}>
            <CardContent sx={{ pb: 1 }}>
              <Stack spacing={2}>
                <Stack spacing={0.5}>
                  <Typography variant="subtitle1">
                    {selectedPublisher?.name ?? "出版社"}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    公式カタログから新しい順に探します
                  </Typography>
                </Stack>
                <FormControl size="small" fullWidth disabled={loading}>
                  <InputLabel id="publisher-select-label">出版社</InputLabel>
                  <Select
                    labelId="publisher-select-label"
                    label="出版社"
                    value={selectedPublisherId}
                    onChange={(event) => {
                      setSelectedPublisherId(event.target.value);
                    }}
                  >
                    {publishers.map((publisher) => (
                      <MenuItem
                        key={publisher.publisherId}
                        value={publisher.publisherId}
                      >
                        {publisher.name}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
                <TextField
                  label="表示結果をタイトルで絞り込み"
                  value={publisherKeyword}
                  onChange={(event) => setPublisherKeyword(event.target.value)}
                  disabled={loading}
                  size="small"
                  slotProps={{
                    input: {
                      startAdornment: (
                        <InputAdornment position="start">
                          <SearchIcon />
                        </InputAdornment>
                      ),
                    },
                  }}
                />
                <Typography variant="body2" color="text.secondary">
                  絞り込みは「本を表示」後の一覧にも反映できます
                </Typography>
              </Stack>
            </CardContent>
            <CardActions sx={{ px: 2, pb: 2 }}>
              <Button
                variant="contained"
                startIcon={<MenuBookIcon />}
                onClick={handlePublisherSearch}
                disabled={loading || !selectedPublisherId}
              >
                本を表示
              </Button>
            </CardActions>
          </Card>
        </Stack>
      )}
      <br />
      {loading ? (
        <CircularProgress />
      ) : (
        <>
          {displayResult(
            books,
            handleSelect,
            searchMode === "publisher"
              ? publisherPagination?.totalCount
              : undefined
          )}
          {searchMode === "publisher" &&
            publisherPagination &&
            publisherPagination.totalPages > 1 && (
              <Stack alignItems="center" sx={{ my: 3 }}>
                <Pagination
                  page={publisherPagination.page}
                  count={publisherPagination.totalPages}
                  onChange={handlePublisherPageChange}
                  color="primary"
                  disabled={loading}
                  showFirstButton
                  showLastButton
                />
              </Stack>
            )}
        </>
      )}
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
