import type { AuthState } from "../../components/contexts/AuthContext";

export const canEditBookMaster = (state: AuthState): boolean => {
  return state.isAuthorized;
};
