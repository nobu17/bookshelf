import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../components/contexts/AuthContext";

export const useSignOut = (): void => {
  const navigate = useNavigate();
  const { state, loading, signOut } = useAuth();

  useEffect(() => {
    const init = async () => {
      if (state.isAuthorized && !loading) {
        await signOut();
        navigate("/");
      }
    };
    init();
  }, [navigate, signOut, state, loading]);
};
