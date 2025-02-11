import { Typography } from "@mui/material";

type PageTitleProps = {
  title: string;
};

export default function PageTitle(props: PageTitleProps) {
  return (
    <>
      <Typography variant="h5" align="center" gutterBottom>
        {props.title}
      </Typography>
    </>
  );
}
