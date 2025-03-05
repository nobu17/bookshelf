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

import { BookInfo, Review, ReviewStateDef } from "../../types/data";
import SubmitButtons from "./SubmitButtons";
import { RhfReviewStateSelect } from "./Rhf/RhfReviewStateSelect";
import { getImageUrl } from "../../libs/utils/image";
import { DateTimePicker } from "@mui/x-date-pickers";
import dayjs from "dayjs";
import timezone from "dayjs/plugin/timezone";
import utc from "dayjs/plugin/utc";
import { useEffect } from "react";

dayjs.extend(utc);
dayjs.extend(timezone);

type BookReviewEditFormProps = {
  bookInfo: BookInfo;
  editItem: Review;
  onSubmit: (review: Review) => void;
  onCancel: () => void;
};

export default function BookReviewEditForm(props: BookReviewEditFormProps) {
  const { editItem, bookInfo, onSubmit, onCancel } = props;
  const {
    register,
    handleSubmit,
    setValue,
    control,
    formState: { errors },
  } = useForm<Review>({ defaultValues: editItem });

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

  const handlePreSubmit = (data: Review) => {
    console.log("pre st", data);
    if (data.state !== ReviewStateDef.Completed) {
      data.completedAt = null;
    }
    console.log("pre", data);
    onSubmit(data);
  };

  return (
    <>
      <Container maxWidth="sm" sx={{ pt: 1 }}>
        <Divider />
        <Stack spacing={3}>
          <Typography variant="subtitle1" align="center">
            書籍名：{bookInfo.title}
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
                  <DateTimePicker
                    {...field}
                    label="読了日"
                    format="YYYY-MM-DD hh:mm"
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
