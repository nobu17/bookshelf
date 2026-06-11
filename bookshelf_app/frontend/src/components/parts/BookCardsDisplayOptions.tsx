import { FormControlLabel, FormGroup, Switch } from "@mui/material";
import Grid from "@mui/material/Grid2";
import { DisplayOption, DisplayOrderOption } from "../../types/display";
import { OrderStateSelect } from "./OrderStateSelect";

type BookCardsDisplayOptionsProps = {
  option: DisplayOption;
  onChange?: (opt: DisplayOption) => void;
};

export default function BookCardsDisplayOptions(
  props: BookCardsDisplayOptionsProps
) {
  const { option, onChange } = props;
  const handleCompleted = (event: React.ChangeEvent<HTMLInputElement>) => {
    fireOptionChange({ ...option, isDisplayComplete: event.target.checked });
  };
  const handleInProgress = (event: React.ChangeEvent<HTMLInputElement>) => {
    fireOptionChange({ ...option, isDisplayInProgress: event.target.checked });
  };
  const handleNotYet = (event: React.ChangeEvent<HTMLInputElement>) => {
    fireOptionChange({ ...option, isDisplayNotYet: event.target.checked });
  };
  const handleOrderChange = (value: DisplayOrderOption) => {
    fireOptionChange({ ...option, order: value });
  };
  const fireOptionChange = (option: DisplayOption) => {
    if (onChange) {
      onChange(option);
    }
  };
  return (
    <>
      <Grid
        container
        spacing={1}
        sx={{
          justifyContent: "center",
          alignItems: "center",
          mb: 2,
        }}
      >
        <FormGroup row={true}>
          <FormControlLabel
            control={
              <Switch
                onChange={handleCompleted}
                checked={option.isDisplayComplete}
              />
            }
            label="読了"
          />
          <FormControlLabel
            control={
              <Switch
                onChange={handleInProgress}
                checked={option.isDisplayInProgress}
              />
            }
            label="読中"
          />
          <FormControlLabel
            control={
              <Switch
                onChange={handleNotYet}
                checked={option.isDisplayNotYet}
              />
            }
            label="未読"
          />
        </FormGroup>
        <OrderStateSelect
          label="表示順"
          value={option.order}
          onChange={handleOrderChange}
        />
      </Grid>
    </>
  );
}
