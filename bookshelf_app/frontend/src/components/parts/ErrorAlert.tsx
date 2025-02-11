import { Alert } from "@mui/material";

type ErrorAlertProps = {
  error: Error;
};

export default function ErrorAlert(props: ErrorAlertProps) {
  return (
    <>
      <Alert variant="filled" severity="error">
        { props.error.message }
      </Alert>
    </>
  );
}
