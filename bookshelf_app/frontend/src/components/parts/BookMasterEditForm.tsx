import { Controller, useForm } from "react-hook-form";
import {
  Box,
  Button,
  Card,
  CardActionArea,
  CardContent,
  CardMedia,
  Container,
  Dialog,
  DialogContent,
  DialogTitle,
  Divider,
  Snackbar,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import { DatePicker } from "@mui/x-date-pickers";
import dayjs from "dayjs";
import SearchIcon from "@mui/icons-material/Search";
import { useState } from "react";

import { BookInfo } from "../../types/data";
import { dateToString } from "../../libs/utils/date";
import { getBookInfoImageUrl, getFallbackImageUrl } from "../../libs/utils/image";
import SubmitButtons from "./SubmitButtons";
import BookSearchApi from "../../libs/apis/bookSearch";
import { BookSearchResult } from "../../types/bookSearch";

type BookMasterEditFormProps = {
  bookInfo: BookInfo;
  onSubmit: (book: BookMasterEditInfo) => void;
  onCancel: () => void;
};

const bookSearchApi = new BookSearchApi();

export type BookMasterEditInfo = {
  isbn13: string;
  title: string;
  publisher: string;
  authorsText: string;
  publishedAt: Date;
  imageUrl: string;
};

export const toBookMasterEditInfo = (book: BookInfo): BookMasterEditInfo => {
  return {
    isbn13: book.isbn13,
    title: book.title,
    publisher: book.publisher,
    authorsText: book.authors.join("\n"),
    publishedAt: book.publishedAt,
    imageUrl: book.imageUrl || "",
  };
};

export const toBookUpdateParameter = (book: BookMasterEditInfo) => {
  return {
    isbn13: book.isbn13,
    title: book.title,
    publisher: book.publisher,
    authors: book.authorsText
      .split(/\r?\n/)
      .map((author) => author.trim())
      .filter((author) => author.length > 0),
    publishedAt: book.publishedAt,
    imageUrl: book.imageUrl.trim() || null,
  };
};

export default function BookMasterEditForm(props: BookMasterEditFormProps) {
  const { bookInfo, onSubmit, onCancel } = props;
  const {
    register,
    handleSubmit,
    control,
    watch,
    setValue,
    formState: { errors },
  } = useForm<BookMasterEditInfo>({
    defaultValues: toBookMasterEditInfo(bookInfo),
  });
  const [searchResults, setSearchResults] = useState<BookSearchResult[]>([]);
  const [isSearchDialogOpen, setIsSearchDialogOpen] = useState(false);
  const [isSearching, setIsSearching] = useState(false);
  const [searchError, setSearchError] = useState<Error | null>(null);

  const imageUrl = watch("imageUrl");
  const isbn13 = watch("isbn13");
  const previewBook = { ...bookInfo, imageUrl: imageUrl || null };
  const handleSearchByIsbn = async () => {
    setIsSearching(true);
    try {
      setSearchError(null);
      const res = await bookSearchApi.search(isbn13);
      setSearchResults(res.data.books);
      setIsSearchDialogOpen(true);
    } catch (e: unknown) {
      if (e instanceof Error) {
        setSearchError(e);
        return;
      }
      setSearchError(new Error("unexpected error."));
    } finally {
      setIsSearching(false);
    }
  };
  const handleSelectSearchResult = (book: BookSearchResult) => {
    setValue("isbn13", book.isbn13);
    setValue("title", book.title);
    setValue("publisher", book.publisher);
    setValue("authorsText", book.authors.join("\n"));
    setValue("publishedAt", book.publishedAt);
    setValue("imageUrl", book.imageUrl || "");
    setIsSearchDialogOpen(false);
  };

  return (
    <Container maxWidth="sm" sx={{ pt: 1 }}>
      <Divider />
      <Stack spacing={3} sx={{ pt: 3 }}>
        <Box
          component="img"
          sx={{ height: "180px", width: "auto", objectFit: "contain" }}
          src={getBookInfoImageUrl(previewBook)}
          onError={(e) => {
            e.currentTarget.src = getFallbackImageUrl();
          }}
        />
        <TextField
          label="ISBN13"
          {...register("isbn13", {
            required: "必須です。",
            pattern: {
              value: /^(978|979)[0-9]{10}$/,
              message: "ISBN13は978または979で始まる13桁の数字です。",
            },
          })}
          error={Boolean(errors.isbn13)}
          helperText={errors.isbn13?.message}
        />
        <Button
          variant="outlined"
          startIcon={<SearchIcon />}
          onClick={handleSearchByIsbn}
          disabled={isSearching || Boolean(errors.isbn13)}
        >
          ISBNで検索
        </Button>
        <TextField
          label="書籍名"
          {...register("title", {
            required: "必須です。",
            maxLength: { value: 100, message: "最大100文字です。" },
          })}
          error={Boolean(errors.title)}
          helperText={errors.title?.message}
        />
        <TextField
          label="出版社"
          {...register("publisher", {
            required: "必須です。",
            maxLength: { value: 100, message: "最大100文字です。" },
          })}
          error={Boolean(errors.publisher)}
          helperText={errors.publisher?.message}
        />
        <TextField
          label="著者"
          multiline
          minRows={3}
          {...register("authorsText", {
            required: "必須です。",
            validate: (value) =>
              value
                .split(/\r?\n/)
                .map((author) => author.trim())
                .filter((author) => author.length > 0).length > 0 ||
              "著者を1件以上入力してください。",
          })}
          error={Boolean(errors.authorsText)}
          helperText={errors.authorsText?.message}
        />
        <Controller
          name="publishedAt"
          control={control}
          render={({ field }) => {
            return (
              <DatePicker
                label="出版日"
                format="YYYY-MM-DD"
                value={dayjs(field.value)}
                onChange={(newValue) => {
                  if (newValue != null) {
                    field.onChange(newValue.toDate());
                  }
                }}
                slotProps={{
                  textField: {
                    helperText: dateToString(field.value),
                  },
                }}
              />
            );
          }}
        />
        <TextField
          label="書影URL"
          {...register("imageUrl", {
            maxLength: { value: 1000, message: "最大1000文字です。" },
          })}
          error={Boolean(errors.imageUrl)}
          helperText={errors.imageUrl?.message}
        />
        <SubmitButtons onSubmit={handleSubmit(onSubmit)} onCancel={onCancel} />
      </Stack>
      <Dialog
        open={isSearchDialogOpen}
        onClose={() => setIsSearchDialogOpen(false)}
        fullWidth
        maxWidth="md"
      >
        <DialogTitle>検索結果</DialogTitle>
        <DialogContent>
          <Stack spacing={2}>
            {searchResults.length === 0 ? (
              <Typography>候補が見つかりませんでした。</Typography>
            ) : (
              searchResults.map((book) => (
                <Card key={`${book.source}:${book.sourceId}`}>
                  <CardActionArea onClick={() => handleSelectSearchResult(book)}>
                    <Stack direction={{ xs: "column", sm: "row" }} spacing={2}>
                      <CardMedia
                        component="img"
                        sx={{
                          width: { xs: "100%", sm: 120 },
                          height: 180,
                          objectFit: "contain",
                          p: 1,
                        }}
                        image={book.imageUrl || getFallbackImageUrl()}
                        onError={(e) => {
                          e.currentTarget.src = getFallbackImageUrl();
                        }}
                      />
                      <CardContent>
                        <Typography fontWeight="bold">{book.title}</Typography>
                        <Typography>ISBN13: {book.isbn13}</Typography>
                        <Typography>出版社: {book.publisher}</Typography>
                        <Typography>著者: {book.authors.join(", ")}</Typography>
                        <Typography>出版日: {dateToString(book.publishedAt)}</Typography>
                      </CardContent>
                    </Stack>
                  </CardActionArea>
                </Card>
              ))
            )}
          </Stack>
        </DialogContent>
      </Dialog>
      <Snackbar
        anchorOrigin={{ vertical: "top", horizontal: "center" }}
        open={searchError ? true : false}
        autoHideDuration={6000}
        message={searchError ? searchError.message : ""}
      />
    </Container>
  );
}
