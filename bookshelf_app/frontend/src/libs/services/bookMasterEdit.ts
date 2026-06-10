import { BookUpdateParameter } from "../apis/books";
import { BookInfo } from "../../types/data";

export type BookMasterEditInfo = {
  isbn13: string;
  title: string;
  publisher: string;
  authorsText: string;
  publishedAt: Date;
  imageUrl: string;
  tagNames: string[];
};

export const toBookMasterEditInfo = (book: BookInfo): BookMasterEditInfo => {
  return {
    isbn13: book.isbn13,
    title: book.title,
    publisher: book.publisher,
    authorsText: book.authors.join("\n"),
    publishedAt: book.publishedAt,
    imageUrl: book.imageUrl || "",
    tagNames: book.tags.map((tag) => tag.name),
  };
};

export const toBookUpdateParameter = (
  book: BookMasterEditInfo
): BookUpdateParameter => {
  return {
    isbn13: book.isbn13,
    title: book.title,
    publisher: book.publisher,
    authors: book.authorsText
      .split(/\r?\n/)
      .map((author) => author.trim())
      .filter((author) => author.length > 0),
    publishedAt: book.publishedAt,
    imageUrl: book.imageUrl.trim() || null,
  };
};
