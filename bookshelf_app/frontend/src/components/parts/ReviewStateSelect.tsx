import { MenuItem, TextField, TextFieldProps } from "@mui/material";
import type { ChangeEventHandler, FocusEventHandler } from "react";

import { ReviewState, toJapanese, AllReviewStates } from "../../types/data";

export type ReviewStateSelectProps = {
  label: string;
  error?: string;
};

export function ReviewStateSelect(
  props: ReviewStateSelectProps & {
    inputRef: TextFieldProps["ref"];
    value: ReviewState;
    onChange: ChangeEventHandler<HTMLTextAreaElement>;
    onBlur: FocusEventHandler<HTMLTextAreaElement>;
  }
) {
  return (
    <>
      <TextField
        ref={props.inputRef}
        onChange={props.onChange}
        onBlur={props.onBlur}
        select
        slotProps={{
          select: {
            multiple: false,
            value: props.value,
          },
        }}
        sx={{ mt: 2 }}
        fullWidth
        label={props.label}
        error={Boolean(props.error)}
        helperText={props.error}
      >
        {AllReviewStates.map((state, index) => (
          <MenuItem key={index} value={state}>
            {toJapanese(state)}
          </MenuItem>
        ))}
      </TextField>
    </>
  );
}
