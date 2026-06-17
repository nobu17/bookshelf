import { Backdrop, Box, CircularProgress, Typography } from "@mui/material";

type LoadingSpinnerProps = {
  isLoading: boolean;
  message?: string;
};

export default function LoadingSpinner(props: LoadingSpinnerProps) {
  return (
    <>
      <Backdrop
        open={props.isLoading}
        sx={{
          color: "common.white",
          zIndex: (theme) => theme.zIndex.modal + 1,
        }}
      >
        <Box
          sx={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            gap: 2,
          }}
        >
          <CircularProgress color="warning" size={70} />
          {props.message ? (
            <Typography color="inherit">{props.message}</Typography>
          ) : null}
        </Box>
      </Backdrop>
    </>
  );
}
