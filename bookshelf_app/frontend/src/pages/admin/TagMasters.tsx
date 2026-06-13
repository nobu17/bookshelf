import { CircularProgress } from "@mui/material";

import TagMastersContainer from "../../components/containers/TagMastersContainer";
import { useAuth } from "../../components/contexts/AuthContext";
import ErrorAlert from "../../components/parts/ErrorAlert";
import { useAuthGuard } from "../../hooks/auth/UseAuthGuard";
import MyPageBase from "../mypage/MyPageBase";

export default function TagMasters() {
  useAuthGuard();
  const { state, loading } = useAuth();

  if (loading) {
    return <CircularProgress />;
  }
  if (!state.isAdmin) {
    return <ErrorAlert error={new Error("管理者権限が必要です。")} />;
  }

  return (
    <MyPageBase title="タグマスタ管理">
      <TagMastersContainer />
    </MyPageBase>
  );
}
