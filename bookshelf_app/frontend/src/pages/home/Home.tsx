import Grid from "@mui/material/Grid2";
import LatestBookReviewsContainer from "../../components/containers/LatestBookReviewsContainer";
import PageTitle from "../../components/parts/PageTitle";

// import BookCard from "../../components/parts/BookCards"

function Home() {
  return (
    <>
      <PageTitle title="最近読んだ本" />
      <Grid container spacing={2}>
        <Grid size={12}>
          <LatestBookReviewsContainer />
        </Grid>
      </Grid>
    </>
  );
}

export default Home;
