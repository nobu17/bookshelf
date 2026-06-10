import { Autocomplete, TextField } from "@mui/material";

import { BookTag } from "../../types/data";
import {
  normalizeBookTagNames,
  validateBookTagNames,
} from "../../libs/services/bookTags";

type BookTagInputProps = {
  label?: string;
  value: string[];
  options: BookTag[];
  onChange: (tagNames: string[]) => void;
};

export default function BookTagInput(props: BookTagInputProps) {
  const { label = "タグ", value, options, onChange } = props;
  const errorMessage = validateBookTagNames(value);

  return (
    <Autocomplete
      multiple
      freeSolo
      options={options.map((tag) => tag.name)}
      value={value}
      onChange={(_, newValue) => {
        onChange(normalizeBookTagNames(newValue));
      }}
      renderInput={(params) => (
        <TextField
          {...params}
          label={label}
          error={Boolean(errorMessage)}
          helperText={errorMessage ?? "Enterで追加できます。"}
        />
      )}
    />
  );
}
