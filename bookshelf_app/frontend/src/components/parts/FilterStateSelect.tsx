import {
  FormControl,
  InputLabel,
  MenuItem,
  Select,
  SelectChangeEvent,
} from "@mui/material";

import {
  AllFilterConditions,
  FilterCondition,
  toJapanese,
} from "../../types/filter";

export type FilterStateSelectProps = {
  label: string;
  value: FilterCondition;
  onSelectionChanged?: (state: FilterCondition) => void;
};

export function FilterStateSelect(props: FilterStateSelectProps) {
  const { label, value, onSelectionChanged } = props;

  const handleChange = (event: SelectChangeEvent) => {
    const select = JSON.parse(event.target.value) as FilterCondition;
    if (onSelectionChanged) {
      onSelectionChanged(select);
    }
  };
  return (
    <>
      <FormControl fullWidth>
        <InputLabel id="condition-select-label">{label}</InputLabel>
        <Select
          labelId="condition-select-label"
          value={JSON.stringify(value)}
          onChange={handleChange}
        >
          {AllFilterConditions.map((cond) => (
            <MenuItem key={cond} value={JSON.stringify(cond)}>
              {toJapanese(cond)}
            </MenuItem>
          ))}
        </Select>
      </FormControl>
    </>
  );
}
