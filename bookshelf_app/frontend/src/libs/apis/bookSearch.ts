import axios from "axios";
import { XMLParser } from "fast-xml-parser";
import { NdlBook } from "../../types/ndls";

const MaxCountSearch = 500;

export const searchNdlBooks = async (keyword: string): Promise<NdlBook[]> => {
  try {
    const url = "https://ndlsearch.ndl.go.jp/api/opensearch";
    const params = {
      any: keyword,
      cnt: MaxCountSearch,
      mediatype: "books",
    };

    const response = await axios.get(url, { params, responseType: "text" });

    const parser = new XMLParser({
      ignoreAttributes: false, // 属性もパース
      attributeNamePrefix: "@_", // 属性のプレフィックス
    });
    const jsonData = parser.parse(response.data);

    let items = jsonData.rss.channel.item || [];

    if (!Array.isArray(items)) {
      items = [items];
    }

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const books = items.map((item: any) => {
      const title = item.title;

      let authors: string[] = [];
      const tempAuthors = item["dc:creator"];
      if (!tempAuthors) {
        authors = ["著者不明"];
      } else if (!Array.isArray(tempAuthors)) {
        authors = [tempAuthors];
      } else {
        authors = tempAuthors;
      }
      // remove comma
      authors = authors.map((author) => {
        return author.replace(/,/g, "");
      });

      let isbn13 = null;
      const identifiers = convertIdentifiers(item);
      isbn13 = identifiers.find((data) => {
        return data.text.startsWith("978");
      });
      if (isbn13) {
        isbn13 = isbn13.text;
      } else {
        const isbn10 = identifiers.find((data) => {
          return data.xType === "dcndl:ISBN";
        });
        if (isbn10) {
          isbn13 = convertIsbn10ToIsbn13(isbn10.text);
        }
      }
      if (isbn13) {
        isbn13 = isbn13.split("-").join("");
      }

      let publisher = "不明";
      if (
        Array.isArray(item["dc:publisher"]) &&
        item["dc:publisher"].length > 0
      ) {
        publisher = item["dc:publisher"][0] || "不明";
      } else {
        publisher = item["dc:publisher"] || "不明";
      }

      // publishedDate format is YYYY.M
      const publishedDate = String(item["dcterms:issued"]) || "不明";
      let pubDate = new Date(1970); // minimum date
      const pubSplits = publishedDate.split(".");
      if (pubSplits.length >= 2) {
        const year = Number(pubSplits[0]);
        const month = Number(pubSplits[1]);
        pubDate = new Date(year, month - 1);
      }
      return { title, authors, isbn13, pubDate, publisher };
    });

    const ndlBooks: NdlBook[] = [];
    for (const book of books) {
      if (!book || !book.isbn13) {
        continue;
      }
      // not allow same isbn
      if (ndlBooks.find(x => x.isbn13 === book.isbn13)) {
        continue;
      }
      ndlBooks.push({
        title: book.title,
        authors: book.authors,
        isbn13: book.isbn13,
        publisher: book.publisher,
        publishedAt: book.pubDate,
      });
    }
    console.log(ndlBooks);
    return ndlBooks;
  } catch (error) {
    console.error("Error fetching data:", error);
    throw error;
  }
};

type Identifier = {
  xType: string;
  text: string;
};

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const convertIdentifiers = (item: any): Identifier[] => {
  const identifiers: Identifier[] = [];
  if (Array.isArray(item["dc:identifier"])) {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    item["dc:identifier"].forEach((data: any) => {
      if (!data["@_xsi:type"] || !data["#text"]) {
        return;
      }
      identifiers.push({
        xType: data["@_xsi:type"],
        text: String(data["#text"]),
      });
    });
  } else if (item["dc:identifier"]) {
    const data = item["dc:identifier"];
    if (data["@_xsi:type"] && data["#text"]) {
      identifiers.push({
        xType: data["@_xsi:type"],
        text: String(data["#text"]),
      });
    }
  }
  return identifiers;
};

const convertIsbn10ToIsbn13 = (isbn10: string): string | null => {
  // ISBN-10のフォーマットを確認
  if (!/^\d{9}[\dX]$/.test(isbn10)) {
    return null; // 無効なISBN-10
  }

  // "978" を前に追加して、チェックデジットを計算
  const isbnBase = "978" + isbn10.slice(0, 9);

  // ISBN-13 のチェックデジットを計算
  const digits = isbnBase.split("").map(Number);
  const checkDigit =
    (10 -
      (digits.reduce(
        (sum, num, idx) => sum + num * (idx % 2 === 0 ? 1 : 3),
        0
      ) %
        10)) %
    10;

  // ISBN-13を返す
  return isbnBase + checkDigit;
};
