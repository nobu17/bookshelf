import axios, { AxiosInstance, AxiosError } from "axios";
import Config from "../utils/config";

export interface ApiResponse<T> {
  data: T;
}

interface ApiErrorImpl {
  error: Error;
  code: number;
  message: string;
  isBadRequest: () => boolean;
  isAuthError: () => boolean;
}

export class ApiError extends Error implements ApiErrorImpl {
  constructor(
    public error: Error,
    public code: number,
    message: string
  ) {
    super(message);
    this.name = "ApiError";
  }

  isBadRequest(): boolean {
    return this.code === 400 || this.code === 422;
  }
  isAuthError(): boolean {
    return this.code === 401;
  }
  isForbidden(): boolean {
    return this.code === 403;
  }
  isNotFound(): boolean {
    return this.code === 404;
  }
}

export default class ApiBase {
  protected _api: AxiosInstance;

  constructor(
    protected _baseUrl: string = "",
    protected _timeOut: number = 0,
    protected _headers: Record<string, string> | null = null
  ) {
    if (this._baseUrl === "") {
      this._baseUrl = Config.apiRoot;
    }
    if (this._timeOut <= 0) {
      this._timeOut = Config.apiTimeout;
    }
    if (!this._headers) {
      this._headers = {
        "Content-Type": "application/json",
        "X-Requested-With": "XMLHttpRequest",
      };
    }
    this._api = axios.create({
      baseURL: this._baseUrl,
      headers: this._headers,
      responseType: "json",
      timeout: this._timeOut,
    });
    this._api.interceptors.request.use(async (request) => {
      if (!request || !request.headers) return request;

      // request.headers.Authorization = `Bearer ${idToken}`;
      return request;
    });
  }

  getAxiosInstance(): AxiosInstance {
    return this._api;
  }

  getAsync<T>(
    url: string,
    converter?: (data: unknown) => ApiResponse<T>
  ): Promise<ApiResponse<T>> {
    return new Promise((resolve, reject) => {
      this._api
        .get(url)
        .then((r) => {
          if (converter) {
            resolve(converter(r.data));
            return;
          }
          const res = {
            data: r.data,
          };
          resolve(res);
        })
        .catch((error) => {
          reject(convertError(error));
        });
    });
  }

  postAsync<T>(url: string, param: unknown): Promise<ApiResponse<T>> {
    const json = JSON.stringify(param);
    return new Promise((resolve, reject) => {
      this._api
        .post(url, json)
        .then((r) => {
          const res = {
            data: r.data,
          };
          resolve(res);
        })
        .catch((error) => {
          reject(convertError(error));
        });
    });
  }

  putAsync(url: string, param: unknown): Promise<void> {
    const json = JSON.stringify(param);
    return new Promise((resolve, reject) => {
      this._api
        .put(url, json)
        .then(() => {
          resolve();
        })
        .catch((error) => {
          reject(convertError(error));
        });
    });
  }

  putAsyncWithResponse<T>(
    url: string,
    param: unknown
  ): Promise<ApiResponse<T>> {
    const json = JSON.stringify(param);
    return new Promise((resolve, reject) => {
      this._api
        .put(url, json)
        .then((r) => {
          resolve({ data: r.data });
        })
        .catch((error) => {
          reject(convertError(error));
        });
    });
  }

  deleteAsync(url: string): Promise<void> {
    return new Promise((resolve, reject) => {
      this._api
        .delete(url)
        .then(() => {
          resolve();
        })
        .catch((error) => {
          reject(convertError(error));
        });
    });
  }
}

export const convertError = (error: unknown): ApiError => {
  if (isAxiosError(error)) {
    const message = getAxiosErrorMessage(error);
    return new ApiError(
      error,
      error.response?.status != null ? error.response?.status : 0,
      message
    );
  }
  const wrapped = error instanceof Error ? error : new Error("unexpected error.");
  return new ApiError(wrapped, 0, wrapped.message || "予期しないエラーが発生しました。");
};

const isAxiosError = (error: unknown): error is AxiosError => {
  return axios.isAxiosError(error);
};

const getAxiosErrorMessage = (error: AxiosError): string => {
  if (error.code === "ECONNABORTED") {
    return "サーバーからの応答がタイムアウトしました。時間を置いて再度お試しください。";
  }

  if (!error.response) {
    return "サーバーに接続できませんでした。ネットワーク状態を確認して再度お試しください。";
  }

  const data = error.response.data;
  if (typeof data === "string") {
    return data;
  }

  if (isErrorResponse(data)) {
    return data.message ?? data.detail ?? "APIリクエストでエラーが発生しました。";
  }

  if (error.response.status === 429) {
    return "外部書籍検索APIの利用制限に達しました。少し時間を置いてから再度お試しください。";
  }

  return error.message || "APIリクエストでエラーが発生しました。";
};

const isErrorResponse = (
  value: unknown
): value is { message?: string; detail?: string } => {
  return (
    typeof value === "object" &&
    value !== null &&
    (("message" in value && typeof value.message === "string") ||
      ("detail" in value && typeof value.detail === "string"))
  );
};

export interface Api {
  getAxiosInstance(): AxiosInstance;
}
