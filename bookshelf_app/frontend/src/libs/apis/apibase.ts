/* eslint-disable @typescript-eslint/no-unused-vars */
/* eslint-disable @typescript-eslint/no-explicit-any */
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
}

export class ApiError implements ApiErrorImpl {
  public name: string;
  constructor(
    public error: Error,
    public code: number,
    public message: string
  ) {
    this.name = "ApiError";
  }

  isBadRequest(): boolean {
    return this.code === 400;
  }
}

export default class ApiBase {
  private _api: AxiosInstance;

  constructor(private _baseUrl: string = "", private _timeOut: number = 0) {
    if (this._baseUrl === "") {
      this._baseUrl = Config.apiRoot;
    }
    if (this._timeOut <= 0) {
      this._timeOut = Config.apiTimeout;
    }
    this._api = axios.create({
      baseURL: this._baseUrl,
      headers: {
        "Content-Type": "application/json",
        "X-Requested-With": "XMLHttpRequest",
      },
      responseType: "json",
      timeout: this._timeOut,
    });
    this._api.interceptors.request.use(async (request) => {
      if (!request || !request.headers) return request;

      // request.headers.Authorization = `Bearer ${idToken}`;
      return request;
    });
  }

  getAsync<T>(url: string, converter?: ((data: any)=> ApiResponse<T>)): Promise<ApiResponse<T>> {
    return new Promise((resolve, reject) => {
      const reqUrl = this._baseUrl + url;
      this._api
        .get(reqUrl)
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

  postAsync<T>(url: string, param: any): Promise<ApiResponse<T>> {
    const json = JSON.stringify(param);
    return new Promise((resolve, reject) => {
      const reqUrl = this._baseUrl + url;
      this._api
        .post(reqUrl, json)
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

  putAsync(url: string, param: any): Promise<void> {
    const json = JSON.stringify(param);
    return new Promise((resolve, reject) => {
      const reqUrl = this._baseUrl + url;
      this._api
        .put(reqUrl, json)
        .then((_) => {
          resolve();
        })
        .catch((error) => {
          reject(convertError(error));
        });
    });
  }

  deleteAsync(url: string): Promise<void> {
    return new Promise((resolve, reject) => {
      const reqUrl = this._baseUrl + url;
      this._api
        .delete(reqUrl)
        .then((_) => {
          resolve();
        })
        .catch((error) => {
          reject(convertError(error));
        });
    });
  }
}

const convertError = (error: any): ApiError => {
  if (isAxiosError(error)) {
    const message =
      typeof error.response?.data === "string" ? error.response?.data : "";
    return new ApiError(
      error,
      error.response?.status != null ? error.response?.status : 0,
      message
    );
  }
  return new ApiError(error, 0, "");
};

const isAxiosError = (error: any): error is AxiosError => {
  return !!error.isAxiosError;
};
