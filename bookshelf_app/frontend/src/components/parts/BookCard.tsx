import CardMedia from "@mui/material/CardMedia";
import Typography from "@mui/material/Typography";
import Box from "@mui/material/Box";
import Stack from "@mui/material/Stack";

type BookCardProps = {
  bookId: string;
  title: string;
  isbn13: string;
  onSelect: (bookId: string) => void;
};

export default function BookCard(props: BookCardProps) {
  const { bookId, title, isbn13, onSelect } = props;
  const getImageUrl = (isbn13: string): string => {
    return `https://ndlsearch.ndl.go.jp/thumbnail/${isbn13}.jpg`;
  };
  return (
    <>
      <Stack
        direction="column"
        spacing={0}
        sx={{
          justifyContent: "center",
          alignItems: "center",
        }}
        onClick={() => onSelect(bookId)}
      >
        <CardMedia
          component="img"
          height="200"
          sx={{ padding: "1em 0em 0em 0em", objectFit: "contain" }}
          image={getImageUrl(isbn13)}
        />
        <Box
          sx={{
            display: "flex",
            justifyContent: "space-between",
          }}
        >
          <Typography
            sx={{
              mb: 2,
              fontWeight: "bold",
              wordBreak: "break-word",
              maxWidth: 200,
            }}
          >
            {title}
          </Typography>
        </Box>
      </Stack>
    </>
  );
}
