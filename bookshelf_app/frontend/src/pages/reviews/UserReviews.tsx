import { useParams } from "react-router-dom";
import Grid from "@mui/material/Grid2";

import SpecificUserBookReviewsContainer from "../../components/containers/SpecificUserBookReviewsContainer";
import PageTitle from "../../components/parts/PageTitle";

function UserReviews() {
  const { id = "" } = useParams();
  return (
    <>
      <PageTitle title="感想" />
      <Grid container spacing={2}>
        <Grid size={12}>
          <SpecificUserBookReviewsContainer userId={id} />
        </Grid>
      </Grid>
    </>
  );
}

export default UserReviews;
