import { useAuthGuard } from "../../hooks/auth/UseAuthGuard";
import MyReviewsContainers from "../../components/containers/MyReviewsContainers";
import MyPageBase from "./MyPageBase";

function MyReviews() {
  useAuthGuard();
  return (
    <>
      <MyPageBase title="レビュー編集" />
      <MyReviewsContainers />
    </>
  );
}

export default MyReviews;
