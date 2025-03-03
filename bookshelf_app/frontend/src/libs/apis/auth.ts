import ApiBase, { convertError } from "./apibase";
import { ApiResponse } from "./apibase";
import { AuthUserInfo, UserToken } from "../../types/data";

type SignInRequest = {
  username: string;
  password: string;
};

export default class AuthApi extends ApiBase {
  async signIn(request: SignInRequest): Promise<ApiResponse<UserToken>> {
    const payload = new FormData();
    payload.append("username", request.username);
    payload.append("password", request.password);
    payload.append("grant_type", "password");
    const headers = { "content-type": "application/x-www-form-urlencoded" };

    return new Promise((resolve, reject) => {
      const reqUrl = this._baseUrl + `/auth/token`;
      this._api
        .post(reqUrl, payload, { headers: headers })
        .then((r) => {
          const res = {
            data: convert(r.data),
          };
          resolve(res);
        })
        .catch((error) => {
          reject(convertError(error));
        });
    });
  }
}

const convert = (raw: ApiUserToken): UserToken => {
  const adjusted: UserToken = { ...raw };
  adjusted.token = raw.access_token;
  adjusted.user.userId = raw.user.user_id;
  return adjusted;
};

type ApiUserToken = UserToken & {
  access_token: string;
  user: ApiAuthUserInfo;
};

type ApiAuthUserInfo = AuthUserInfo & {
  user_id: string;
};
