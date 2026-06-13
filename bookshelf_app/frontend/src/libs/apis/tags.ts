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

  async update(
    tagId: string,
    name: string
  ): Promise<ApiResponse<TagUpdateResponse>> {
    const res = await this.putAsyncWithResponse<ApiBookTag>(`/tags/${tagId}`, {
      name,
    });
    return { data: convertToBookTag(res.data) };
  }

  async delete(tagId: string): Promise<void> {
    await this.deleteAsync(`/tags/${tagId}`);
  }
}

type TagsFindResponse = {
  tags: BookTag[];
};

type TagCreateResponse = BookTag;

type TagUpdateResponse = BookTag;
