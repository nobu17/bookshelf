import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../components/contexts/AuthContext";

export const useAuthGuard = (): void => {
  const navigate = useNavigate();
  const { state, loading } = useAuth();

  useEffect(() => {
    if (loading) return;
    // when not authorized, back to sign in page
    if (!state.isAuthorized) {
      navigate("/auth/signin");
    }
  }, [navigate, state, loading]);
};
