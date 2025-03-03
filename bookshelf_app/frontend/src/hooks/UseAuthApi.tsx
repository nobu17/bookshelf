import { useEffect } from "react";
import { Api } from "../libs/apis/apibase";
import { getCurrentAuth } from "../libs/services/authStorage";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../components/contexts/AuthContext";

export default function useAuthApi<T extends Api>(api: T) {
  const navigate = useNavigate();
  const { resetAuth } = useAuth();
  useEffect(() => {
    const requestIntercept = api.getAxiosInstance().interceptors.request.use(
      async (request) => {
        if (!request || !request.headers) return request;

        const currentAuth = getCurrentAuth();
        if (!currentAuth) {
          return request;
        }
        request.headers.Authorization = `Bearer ${currentAuth.token}`;
        return request;
      },
      (error) => Promise.reject(error)
    );

    const responseIntercept = api.getAxiosInstance().interceptors.response.use(
      (response) => response,
      async (error) => {
        if (
          error?.response?.status === 403 ||
          error?.response?.status === 401
        ) {
          resetAuth();
          await navigate("/auth/signin");
        }
        return Promise.reject(error);
      }
    );

    return () => {
      api.getAxiosInstance().interceptors.request.eject(requestIntercept);
      api.getAxiosInstance().interceptors.response.eject(responseIntercept);
    };
  }, [api, resetAuth, navigate]);
}
