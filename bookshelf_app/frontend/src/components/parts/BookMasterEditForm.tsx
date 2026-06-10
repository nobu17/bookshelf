import { Controller, useForm } from "react-hook-form";
import {
  Box,
  Button,
  Container,
  Divider,
  Snackbar,
  Stack,
  TextField,
} from "@mui/material";
import { DatePicker } from "@mui/x-date-pickers";
import dayjs from "dayjs";
import SearchIcon from "@mui/icons-material/Search";

import { BookInfo } from "../../types/data";
import { dateToString } from "../../libs/utils/date";
import { getBookInfoImageUrl, getFallbackImageUrl } from "../../libs/utils/image";
import SubmitButtons from "./SubmitButtons";
import { BookSearchResult } from "../../types/bookSearch";
import useBookMasterIsbnSearch from "../../hooks/UseBookMasterIsbnSearch";
import BookMasterSearchResultDialog from "./dialogs/BookMasterSearchResultDialog";
import {
  BookMasterEditInfo,
  toBookMasterEditInfo,
} from "../../libs/services/bookMasterEdit";
import BookTagEditor from "./BookTagEditor";

type BookMasterEditFormProps = {
  bookInfo: BookInfo;
  onSubmit: (book: BookMasterEditInfo) => void;
  onCancel: () => void;
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
  const {
    results: searchResults,
    isDialogOpen: isSearchDialogOpen,
    isSearching,
    error: searchError,
    searchByIsbn,
    closeDialog: closeSearchDialog,
  } = useBookMasterIsbnSearch();

  const imageUrl = watch("imageUrl");
  const isbn13 = watch("isbn13");
  const tagNames = watch("tagNames");
  const previewBook = { ...bookInfo, imageUrl: imageUrl || null };
  const handleSearchByIsbn = async () => {
    await searchByIsbn(isbn13);
  };
  const handleSelectSearchResult = (book: BookSearchResult) => {
    setValue("isbn13", book.isbn13);
    setValue("title", book.title);
    setValue("publisher", book.publisher);
    setValue("authorsText", book.authors.join("\n"));
    setValue("publishedAt", book.publishedAt);
    setValue("imageUrl", book.imageUrl || "");
    closeSearchDialog();
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
        <BookTagEditor
          bookInfo={previewBook}
          value={tagNames}
          onChange={(newTagNames) => setValue("tagNames", newTagNames)}
        />
        <SubmitButtons onSubmit={handleSubmit(onSubmit)} onCancel={onCancel} />
      </Stack>
      <BookMasterSearchResultDialog
        open={isSearchDialogOpen}
        books={searchResults}
        onSelect={handleSelectSearchResult}
        onClose={closeSearchDialog}
      />
      <Snackbar
        anchorOrigin={{ vertical: "top", horizontal: "center" }}
        open={searchError ? true : false}
        autoHideDuration={6000}
        message={searchError ? searchError.message : ""}
      />
    </Container>
  );
}
