import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../components/contexts/AuthContext";

export const useSignInGuard = (): void => {
  const navigate = useNavigate();
  const { state, loading } = useAuth();

  useEffect(() => {
    // when already authorized, back to my page
    if (state.isAuthorized && !loading) {
      navigate("/mypage");
    }
  }, [navigate, state, loading]);
};
