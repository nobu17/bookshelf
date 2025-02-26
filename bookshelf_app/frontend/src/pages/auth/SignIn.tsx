import Grid from "@mui/material/Grid2";
import LoginContainers from "../../components/containers/LoginContainers";
import PageTitle from "../../components/parts/PageTitle";

function SignIn() {
  return (
    <>
      <PageTitle title="ログイン" />
      <Grid container spacing={2}>
        <Grid size={12}>
          <LoginContainers></LoginContainers>
        </Grid>
      </Grid>
    </>
  );
}

export default SignIn;
