import {
  DeepMap,
  FieldError,
  FieldValues,
  useController,
  UseControllerProps,
} from "react-hook-form";

import {
  ReviewStateSelect,
  ReviewStateSelectProps,
} from "../ReviewStateSelect";

export type RhfReviewStateSelectProps<T extends FieldValues> =
  ReviewStateSelectProps & UseControllerProps<T>;

export const RhfReviewStateSelect = <T extends FieldValues>(
  props: RhfReviewStateSelectProps<T>
) => {
  const { name, label, control } = props;
  const {
    field: { ref, ...rest },
    formState: { errors },
  } = useController<T>({
    name,
    control,
    rules: {
      required: { value: true, message: "1つ以上の曜日を選択してください。" },
    },
  });

  return (
    <ReviewStateSelect
      inputRef={ref}
      {...rest}
      label={label}
      error={
        errors[name] &&
        `${(errors[name] as DeepMap<FieldValues, FieldError>).message}`
      }
    />
  );
};
