export const toError = (value: unknown): Error => {
  if (value instanceof Error) {
    return value;
  }
  return new Error("unexpected error.");
};
