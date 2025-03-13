import * as React from "react";
import { createContext, useContext, useEffect, useState } from "react";
import AuthApi from "../../libs/apis/auth";
import { ApiError } from "../../libs/apis/apibase";
import {
  storeAuth,
  clearAuth,
  restoreAuth,
} from "../../libs/services/authStorage";
import { UserToken } from "../../types/data";

type AuthState = {
  isAuthorized: boolean;
  isAdmin: boolean;
  userId: string;
};

type ContextType = {
  state: AuthState;
  loading: boolean;
  signIn: (email: string, password: string) => Promise<void>;
  signOut: () => Promise<void>;
  resetAuth: () => void;
  error: AuthError;
};

const initialState = {
  isAuthorized: false,
  isAdmin: false,
  userId: "",
};

const AuthContext = createContext({} as ContextType);

interface AuthContextProviderProps {
  children?: React.ReactNode;
}

// eslint-disable-next-line react-refresh/only-export-components
export function useAuth(): ContextType {
  return useContext(AuthContext);
}

// eslint-disable-next-line @typescript-eslint/no-unused-vars
const AuthErrors = ["Normal", "Unexpected"] as const;
type AuthErrorDef = (typeof AuthErrors)[number];
export type AuthError = AuthErrorDef | null;

const api = new AuthApi();

export const AuthContextProvider = ({ children }: AuthContextProviderProps) => {
  const [state, setState] = useState(initialState);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<AuthError>(null);

  useEffect(() => {
    const storedInfo = restoreAuth();
    if (storedInfo) {
      setAuthState(storedInfo);
    }
    setLoading(false);
  }, []);

  const signIn = async (email: string, password: string): Promise<void> => {
    setLoading(true);
    try {
      const result = await api.signIn({ username: email, password });
      if (!result.data) {
        throw new Error("unexpected no error");
      }
      setError(null);
      storeAuth(result.data);
      setAuthState(result.data);
    } catch (e: unknown) {
      if (e instanceof ApiError) {
        if (e.isAuthError() || e.isBadRequest()) {
          setError("Normal");
          return;
        }
      }
      setError("Unexpected");
    } finally {
      setLoading(false);
    }
  };

  const signOut = (): Promise<void> => {
    return new Promise((resolve, reject) => {
      try {
        resetAuth();
        resolve();
      } catch (e: unknown) {
        reject(e);
      }
    });
  };

  const resetAuth = () => {
    clearAuth();
    setState(initialState);
  };

  const setAuthState = (token: UserToken) => {
    setState({
      isAuthorized: token.user ? true : false,
      isAdmin: token.user.roles.find((x) => x === "admin") ? true : false,
      userId: token.user.userId,
    });
  };

  const values = {
    state,
    loading,
    signIn,
    signOut,
    resetAuth,
    error,
  };

  return <AuthContext.Provider value={values}>{children}</AuthContext.Provider>;
};
