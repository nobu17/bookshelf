import { CircularProgress } from "@mui/material";

import BookMastersContainer from "../../components/containers/BookMastersContainer";
import { useAuth } from "../../components/contexts/AuthContext";
import ErrorAlert from "../../components/parts/ErrorAlert";
import { useAuthGuard } from "../../hooks/auth/UseAuthGuard";
import MyPageBase from "../mypage/MyPageBase";

export default function BookMasters() {
  useAuthGuard();
  const { state, loading } = useAuth();

  if (loading) {
    return <CircularProgress />;
  }
  if (!state.isAdmin) {
    return <ErrorAlert error={new Error("管理者権限が必要です。")} />;
  }

  return (
    <>
      <MyPageBase title="書籍マスタ管理">
        <BookMastersContainer />
      </MyPageBase>
    </>
  );
}
