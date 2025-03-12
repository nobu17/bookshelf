import { Controller, useForm, useWatch } from "react-hook-form";
import {
  Checkbox,
  Container,
  FormControlLabel,
  Stack,
  TextField,
  Divider,
  Typography,
  Box,
} from "@mui/material";

import { ReviewState, ReviewStateDef } from "../../types/data";
import SubmitButtons from "./SubmitButtons";
import { RhfReviewStateSelect } from "./Rhf/RhfReviewStateSelect";
import { getImageUrl } from "../../libs/utils/image";
import { DatePicker } from "@mui/x-date-pickers";
import dayjs from "dayjs";
import timezone from "dayjs/plugin/timezone";
import utc from "dayjs/plugin/utc";
import { useEffect } from "react";
import { dateToString } from "../../libs/utils/date";

dayjs.extend(utc);
dayjs.extend(timezone);

type BookInfoForDisplay = {
  isbn13: string;
  title: string;
  publisher: string;
  authors: string[];
  publishedAt: Date;
};

type BookReviewEditFormProps = {
  bookInfo: BookInfoForDisplay;
  editItem: ReviewEditInfo;
  onSubmit: (review: ReviewEditInfo) => void;
  onCancel: () => void;
};

export type ReviewEditInfo = {
  content: string;
  isDraft: boolean;
  state: ReviewState;
  completedAt: Date | null;
};

export default function BookReviewEditForm(props: BookReviewEditFormProps) {
  const { editItem, bookInfo, onSubmit, onCancel } = props;
  const {
    register,
    handleSubmit,
    setValue,
    control,
    formState: { errors },
  } = useForm<ReviewEditInfo>({ defaultValues: editItem });

  const state = useWatch({ control, name: "state" });

  useEffect(() => {
    if (state !== ReviewStateDef.Completed) {
      return;
    }
    if (editItem.completedAt !== null) {
      return;
    }
    setValue("completedAt", dayjs().tz("Asia/Tokyo").toDate());
  }, [setValue, state, editItem.completedAt]);

  const handlePreSubmit = (data: ReviewEditInfo) => {
    if (data.state !== ReviewStateDef.Completed) {
      data.completedAt = null;
    }
    onSubmit(data);
  };

  return (
    <>
      <Container maxWidth="sm" sx={{ pt: 1 }}>
        <Divider />
        <Stack spacing={3}>
          <Typography variant="subtitle1" align="left">
            書籍名：{bookInfo.title}
            <br />
            出版社：{bookInfo.publisher}
            <br />
            著者：{bookInfo.authors.join(": ")}
            <br />
            出版年：{dateToString(bookInfo.publishedAt)}
          </Typography>
          <Box
            component="img"
            sx={{ height: "150px", width: "auto", objectFit: "contain" }}
            src={getImageUrl(bookInfo.isbn13)}
          />
          <Divider />
          <TextField
            label="感想, レビュー"
            multiline
            rows={4}
            {...register("content", {
              maxLength: { value: 9999, message: "最大文字数を超えています。" },
            })}
            error={Boolean(errors.content)}
            helperText={errors.content && errors.content.message}
          />
          <RhfReviewStateSelect
            label="読書状態"
            name="state"
            control={control}
          />
          {state === ReviewStateDef.Completed ? (
            <Controller
              name="completedAt"
              control={control}
              render={({ field }) => {
                return (
                  <DatePicker
                    {...field}
                    label="読了日"
                    format="YYYY-MM-DD"
                    {...field}
                    value={dayjs(field.value)}
                    onChange={(newValue) => {
                      if (newValue != null) {
                        field.onChange(newValue.toDate());
                      }
                    }}
                  />
                );
              }}
            />
          ) : (
            <></>
          )}

          <FormControlLabel
            control={
              <Controller
                defaultValue={true}
                name="isDraft"
                control={control}
                render={({ field: { onChange, value, ref } }) => (
                  <Checkbox
                    inputRef={ref}
                    checked={value}
                    onChange={onChange}
                  />
                )}
              />
            }
            label="下書き"
          />
          <SubmitButtons
            onSubmit={handleSubmit(handlePreSubmit)}
            onCancel={onCancel}
          />
        </Stack>
      </Container>
    </>
  );
}
