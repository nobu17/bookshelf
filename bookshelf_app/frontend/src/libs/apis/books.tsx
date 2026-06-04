import { BookInfo, BookTag } from "../../types/data";
import { dateToString, toDate } from "../utils/date";
import ApiBase, { ApiResponse } from "./apibase";

export default class BooksApi extends ApiBase {
  async findByIsbn13(isbn13: string): Promise<ApiResponse<BookFindResponse>> {
    const res = await this.getAsync<ApiBookFindResponse>(
      `/books/isbn13/${isbn13}`
    );
    return { data: convertToBookFindResponse(res.data) };
  }
  async create(
    createBook: BookCreateParameter
  ): Promise<ApiResponse<BookCreateResponse>> {
    const res = await this.postAsync<ApiBookInfo>(
      `/books`,
      convertToApiBookCreateParameter(createBook)
    );
    return { data: convertTiBookCreateResponse(res.data) };
  }
  async update(
    bookId: string,
    updateBook: BookUpdateParameter
  ): Promise<ApiResponse<BookUpdateResponse>> {
    const res = await this.putAsyncWithResponse<ApiBookInfo>(
      `/books/${bookId}`,
      convertToApiBookUpdateParameter(updateBook)
    );
    return { data: convertTiBookUpdateResponse(res.data) };
  }
}

type BookFindResponse = {
  books: BookInfo[];
};

type ApiBookFindResponse = {
  books: ApiBookInfo[];
};

type BookCreateResponse = BookInfo & {};

type BookUpdateResponse = BookInfo & {};

type ApiBookInfo = {
  book_id: string;
  isbn13: string;
  title: string;
  publisher: string;
  authors: string[];
  published_at: string;
  image_url: string;
  tags: BookTag[];
};

const convertToBookFindResponse = (
  info: ApiBookFindResponse
): BookFindResponse => {
  return { books: info.books.map((x) => convertTotBookInfo(x)) };
};

const convertTiBookCreateResponse = (info: ApiBookInfo): BookCreateResponse => {
  return convertTotBookInfo(info);
};

const convertTiBookUpdateResponse = (info: ApiBookInfo): BookUpdateResponse => {
  return convertTotBookInfo(info);
};

const convertTotBookInfo = (info: ApiBookInfo): BookInfo => {
  return {
    bookId: info.book_id,
    isbn13: info.isbn13,
    title: info.title,
    publisher: info.publisher,
    authors: info.authors,
    publishedAt: toDate(info.published_at),
    imageUrl: info.image_url || null,
    tags: info.tags,
  };
};

export type BookCreateParameter = {
  isbn13: string;
  title: string;
  publisher: string;
  authors: string[];
  publishedAt: Date;
  imageUrl?: string | null;
};

export type BookUpdateParameter = BookCreateParameter & {};

type ApiBookCreateParameter = {
  isbn13: string;
  title: string;
  publisher: string;
  authors: string[];
  published_at: string;
  image_url: string;
};

const convertToApiBookCreateParameter = (
  param: BookCreateParameter
): ApiBookCreateParameter => {
  return {
    isbn13: param.isbn13,
    title: param.title,
    publisher: param.publisher,
    authors: param.authors,
    published_at: dateToString(param.publishedAt),
    image_url: param.imageUrl || "",
  };
};

const convertToApiBookUpdateParameter = (
  param: BookUpdateParameter
): ApiBookCreateParameter => {
  return convertToApiBookCreateParameter(param);
};
