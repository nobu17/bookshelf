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

export const filterBooksByKeyword = (
  books: BookWithReviews[],
  keyword: string
): BookWithReviews[] => {
  const words = normalizeSearchText(keyword).split(/\s+/).filter(Boolean);
  if (words.length === 0) {
    return books;
  }

  return books.filter((book) => {
    const target = normalizeSearchText(
      [
        book.title,
        book.publisher,
        ...book.authors,
        ...book.tags.map((tag) => tag.name),
      ].join(" ")
    );
    return words.every((word) => target.includes(word));
  });
};

const normalizeSearchText = (value: string): string => {
  return value.normalize("NFKC").trim().toLocaleLowerCase();
};
