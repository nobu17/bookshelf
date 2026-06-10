import BooksApi from "../apis/books";
import TagsApi from "../apis/tags";
import { BookTag } from "../../types/data";
import { ApiError } from "../apis/apibase";

export const MAX_BOOK_TAGS = 10;
export const MAX_BOOK_TAG_NAME_LENGTH = 15;

export const normalizeBookTagName = (name: string): string => {
  return name.trim();
};

export const normalizeBookTagNames = (names: string[]): string[] => {
  const normalized: string[] = [];
  for (const name of names) {
    const trimmed = normalizeBookTagName(name);
    if (!trimmed) {
      continue;
    }
    if (normalized.includes(trimmed)) {
      continue;
    }
    normalized.push(trimmed);
  }
  return normalized;
};

export const validateBookTagNames = (names: string[]): string | null => {
  const normalized = normalizeBookTagNames(names);
  if (normalized.length > MAX_BOOK_TAGS) {
    return `タグは最大${MAX_BOOK_TAGS}個です。`;
  }
  const overLimit = normalized.find(
    (name) => name.length > MAX_BOOK_TAG_NAME_LENGTH
  );
  if (overLimit) {
    return `タグは最大${MAX_BOOK_TAG_NAME_LENGTH}文字です。`;
  }
  return null;
};

export const resolveBookTags = async (
  tagsApi: TagsApi,
  tagNames: string[]
): Promise<BookTag[]> => {
  const normalized = normalizeBookTagNames(tagNames);
  const validationError = validateBookTagNames(normalized);
  if (validationError) {
    throw new Error(validationError);
  }
  const existing = (await tagsApi.list()).data.tags;
  const resolved: BookTag[] = [];

  for (const name of normalized) {
    const found = existing.find((tag) => tag.name === name);
    if (found) {
      resolved.push(found);
      continue;
    }
    resolved.push(await createOrFindTag(tagsApi, name));
  }

  return resolved;
};

export const updateBookTagsByNames = async (
  booksApi: BooksApi,
  tagsApi: TagsApi,
  bookId: string,
  tagNames: string[]
): Promise<BookTag[]> => {
  const resolved = await resolveBookTags(tagsApi, tagNames);
  await booksApi.updateTags(
    bookId,
    resolved.map((tag) => tag.id)
  );
  return resolved;
};

export const mergeBookTagsByNames = async (
  booksApi: BooksApi,
  tagsApi: TagsApi,
  bookId: string,
  currentTags: BookTag[],
  tagNamesToAdd: string[]
): Promise<BookTag[]> => {
  const resolvedToAdd = await resolveBookTags(tagsApi, tagNamesToAdd);
  const merged = [...currentTags];
  for (const tag of resolvedToAdd) {
    if (!merged.some((current) => current.id === tag.id)) {
      merged.push(tag);
    }
  }
  await booksApi.updateTags(
    bookId,
    merged.map((tag) => tag.id)
  );
  return merged;
};

const createOrFindTag = async (
  tagsApi: TagsApi,
  name: string
): Promise<BookTag> => {
  try {
    return (await tagsApi.create(name)).data;
  } catch (e: unknown) {
    if (e instanceof ApiError && e.code === 409) {
      const latest = (await tagsApi.list()).data.tags;
      const found = latest.find((tag) => tag.name === name);
      if (found) {
        return found;
      }
    }
    throw e;
  }
};
