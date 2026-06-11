import { BookTag, BookWithReviews } from "../../types/data";

export const filterBooksByTag = (
  books: BookWithReviews[],
  tag: BookTag | null
): BookWithReviews[] => {
  if (!tag) {
    return books;
  }

  return books.filter((book) =>
    book.tags.some((bookTag) => bookTag.id === tag.id)
  );
};
