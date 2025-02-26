import { UserToken } from "../../types/data";

const StorageKey = "AuthKey";

export const storeAuth = (auth: UserToken) => {
  localStorage.setItem(StorageKey, JSON.stringify(auth));
};

export const clearAuth = () => {
  localStorage.removeItem(StorageKey);
};

export const restoreAuth = (): UserToken | null => {
  try {
    const json = localStorage.getItem(StorageKey);
    if (json) {
      return JSON.parse(json) as UserToken;
    }
  } catch (e) {
    console.error("failed to restore. reset data.", e);
    clearAuth();
  }

  return null;
};
