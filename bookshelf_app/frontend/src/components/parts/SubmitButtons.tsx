import { Button } from "@mui/material";
import Grid from "@mui/material/Grid2";

type SubmitButtonsProps = {
  onSubmit: callbackSubmit;
  onCancel: callbackCancel;
};
interface callbackSubmit {
  (): void;
}
interface callbackCancel {
  (): void;
}

export default function SubmitButtons(props: SubmitButtonsProps) {
  return (
    <>
      <Grid
        container
        spacing={2}
        sx={{
          justifyContent: "center",
          alignItems: "stretch",
        }}
      >
        <Grid size={6}>
          <Button
            fullWidth
            color="error"
            variant="contained"
            size="large"
            onClick={props.onCancel}
          >
            キャンセル
          </Button>
        </Grid>
        <Grid size={6}>
          <Button
            fullWidth
            color="primary"
            variant="contained"
            size="large"
            onClick={props.onSubmit}
          >
            確定
          </Button>
        </Grid>
      </Grid>
    </>
  );
}
