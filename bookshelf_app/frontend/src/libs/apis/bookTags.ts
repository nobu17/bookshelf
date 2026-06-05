import { BookTag } from "../../types/data";

export type ApiBookTag = {
  id?: string;
  tag_id?: string;
  name: string;
};

export const convertToBookTag = (tag: ApiBookTag): BookTag => {
  return {
    id: tag.id ?? tag.tag_id ?? "",
    name: tag.name,
  };
};

export const convertToBookTags = (tags: ApiBookTag[] | undefined): BookTag[] => {
  return (tags ?? []).map((tag) => convertToBookTag(tag));
};
