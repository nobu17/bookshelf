import { MenuItem, TextField } from "@mui/material";

import {
  AllFilterConditions,
  DisplayOrderOption,
  toJapanese,
} from "../../types/display";

export type OrderStateSelectProps = {
  label: string;
  value: DisplayOrderOption;
  onChange: (value: DisplayOrderOption) => void;
};

export function OrderStateSelect(props: OrderStateSelectProps) {
  return (
    <>
      <TextField
        select
        slotProps={{
          select: {
            multiple: false,
            value: props.value,
          },
        }}
        fullWidth
        label={props.label}
        onChange={(e) => {
          // e.target.value は string 型なので、Number に変換
          const value = Number(e.target.value) as DisplayOrderOption;
          props.onChange(value);
        }}
      >
        {AllFilterConditions.map((state, index) => (
          <MenuItem key={index} value={state}>
            {toJapanese(state)}
          </MenuItem>
        ))}
      </TextField>
    </>
  );
}
