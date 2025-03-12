import Grid from "@mui/material/Grid2";
import PageMenu, { PageMenuProps } from "../../components/parts/PageMenu";
import { useAuth } from "../contexts/AuthContext";
import { useEffect } from "react";

const myReviewBaseUrl = "/reviews/user/";

const bookDisplayMenu: PageMenuProps = {
  title: "マイレビュー",
  icon: "science",
  pageInfoList: [
    { title: "マイレビュー一覧(編集)", url: "/mypage/reviews" },
    { title: "マイレビュー表示", url: myReviewBaseUrl },
    { title: "検索", url: "/mypage/book/search" },
  ],
};

export default function MyHomeContainer() {
  const { state } = useAuth();

  useEffect(() => {
    // update menu Url
    const myReviewPage = bookDisplayMenu.pageInfoList.find(
      (x) => x.title === "マイレビュー表示"
    );
    if (state.isAuthorized) {
      if (myReviewPage) {
        myReviewPage.url = myReviewBaseUrl + state.userId;
        return;
      }
    }
    if (myReviewPage) {
      myReviewPage.url = myReviewBaseUrl;
    }
  }, [state]);

  return (
    <>
      <Grid container spacing={2}>
        <Grid size={{ xs: 12, md: 6 }}>
          <PageMenu {...bookDisplayMenu}></PageMenu>
        </Grid>
      </Grid>
    </>
  );
}
