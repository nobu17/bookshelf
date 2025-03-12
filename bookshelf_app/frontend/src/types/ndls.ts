import { Review } from "./data";

export type NdlBook = {
  title: string;
  authors: string[];
  publisher: string;
  isbn13: string;
  publishedAt: Date;
};

export type NdlBookWithReviews = NdlBook & {
  reviews: Review[];
};