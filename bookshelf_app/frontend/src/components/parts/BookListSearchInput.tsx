import ClearIcon from "@mui/icons-material/Clear";
import SearchIcon from "@mui/icons-material/Search";
import {
  Box,
  IconButton,
  InputAdornment,
  TextField,
  Tooltip,
} from "@mui/material";

type BookListSearchInputProps = {
  value: string;
  onChange: (value: string) => void;
};

export default function BookListSearchInput(props: BookListSearchInputProps) {
  const { value, onChange } = props;

  return (
    <Box sx={{ display: "flex", justifyContent: "center", mx: 1, mb: 2 }}>
      <TextField
        label="書籍検索"
        placeholder="書名・著者・出版社・タグで検索"
        value={value}
        onChange={(event) => onChange(event.target.value)}
        fullWidth
        sx={{ maxWidth: 720 }}
        slotProps={{
          input: {
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon fontSize="small" />
              </InputAdornment>
            ),
            endAdornment: value ? (
              <InputAdornment position="end">
                <Tooltip title="検索条件をクリア">
                  <IconButton
                    aria-label="clear-search-keyword"
                    edge="end"
                    size="small"
                    onClick={() => onChange("")}
                  >
                    <ClearIcon fontSize="small" />
                  </IconButton>
                </Tooltip>
              </InputAdornment>
            ) : undefined,
          },
        }}
      />
    </Box>
  );
}
