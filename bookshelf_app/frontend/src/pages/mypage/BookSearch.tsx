import { useAuthGuard } from "../../hooks/auth/UseAuthGuard";
import MyPageBase from "./MyPageBase";
import SearchBooksContainer from "../../components/containers/SearchBooksContainer";

function BookSearch() {
  useAuthGuard();
  return (
    <>
      <MyPageBase title="検索" />
      <SearchBooksContainer />
    </>
  );
}

export default BookSearch;
