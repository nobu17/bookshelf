/// <reference types="react-scripts" />

declare namespace NodeJS {
  interface ProcessEnv {
    REACT_APP_API_ROOT: string;
    REACT_APP_API_TIMEOUT: number;
  }
}
