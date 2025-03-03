import { UserToken } from "../../types/data";

const StorageKey = "AuthKey";

export const storeAuth = (auth: UserToken) => {
  localStorage.setItem(StorageKey, JSON.stringify(auth));
  globalCache.auth = auth;
};

export const clearAuth = () => {
  localStorage.removeItem(StorageKey);
  globalCache.auth = null;
};

export const restoreAuth = (): UserToken | null => {
  try {
    const json = localStorage.getItem(StorageKey);
    if (json) {
      const data = JSON.parse(json) as UserToken;
      globalCache.auth = data;
      return data;
    }
  } catch (e) {
    console.error("failed to restore. reset data.", e);
    clearAuth();
  }

  return null;
};

const globalCache: { auth: UserToken | null } =
  (// eslint-disable-next-line @typescript-eslint/no-explicit-any
  (globalThis as any)._authCache ??= { auth: null });

export const getCurrentAuth = (): UserToken | null => {
  return globalCache.auth;
};
