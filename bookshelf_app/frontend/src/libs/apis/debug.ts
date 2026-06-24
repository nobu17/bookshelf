import ApiBase, { ApiResponse } from "./apibase";

export type CacheClearResponse = {
  deletedCount: number;
};

type ApiCacheClearResponse = {
  deleted_count: number;
};

export default class DebugApi extends ApiBase {
  async clearPublisherCatalogCache(): Promise<ApiResponse<CacheClearResponse>> {
    const res = await this._api.delete<ApiCacheClearResponse>(
      "/book_search/cache/publisher-catalog"
    );
    return { data: { deletedCount: res.data.deleted_count } };
  }

  async clearBookMetadataCache(): Promise<ApiResponse<CacheClearResponse>> {
    const res = await this._api.delete<ApiCacheClearResponse>(
      "/book_search/cache/book-metadata"
    );
    return { data: { deletedCount: res.data.deleted_count } };
  }
}
