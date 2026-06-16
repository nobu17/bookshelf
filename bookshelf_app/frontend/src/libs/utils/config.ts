const url = import.meta.env.VITE_APP_API_ROOT
const timeOut = import.meta.env.VITE_APP_API_TIMEOUT

type _Config = {
  apiRoot: string;
  apiTimeout: number;
};

const Config: _Config = {
  apiRoot: url || "/api",
  apiTimeout: Number(timeOut) || 15000
};

export default Config;
