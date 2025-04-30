import { FormControlLabel, FormGroup, Switch } from "@mui/material";
import Grid from "@mui/material/Grid2";
import { DisplayOption } from "../../types/dsiplay";

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
      </Grid>
    </>
  );
}
