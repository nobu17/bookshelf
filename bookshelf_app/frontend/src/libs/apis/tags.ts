import { BookTag } from "../../types/data";
import ApiBase, { ApiResponse } from "./apibase";
import { ApiBookTag, convertToBookTag, convertToBookTags } from "./bookTags";

export default class TagsApi extends ApiBase {
  async list(): Promise<ApiResponse<TagsFindResponse>> {
    const res = await this.getAsync<ApiBookTag[]>(`/tags`);
    return { data: { tags: convertToBookTags(res.data) } };
  }

  async create(name: string): Promise<ApiResponse<TagCreateResponse>> {
    const res = await this.postAsync<ApiBookTag>(`/tags`, { name });
    return { data: convertToBookTag(res.data) };
  }
}

type TagsFindResponse = {
  tags: BookTag[];
};

type TagCreateResponse = BookTag;
