import { useAuthGuard } from "../../hooks/auth/UseAuthGuard";
import MyPageBase from "./MyPageBase";
import SearchBooksContainer from "../../components/containers/SearchBooksContainer";

function BookSearch() {
  useAuthGuard();
  return (
    <>
      <MyPageBase title="レビュー投稿(本を探す)" />
      <SearchBooksContainer />
    </>
  );
}

export default BookSearch;
