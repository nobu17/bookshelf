import Grid from "@mui/material/Grid2";
import { Button, InputAdornment, TextField } from "@mui/material";
import SearchIcon from "@mui/icons-material/Search";
import { useForm } from "react-hook-form";

type BookSearchInputProps = {
  word: string;
  isLoading: boolean;
  onSubmit: (word: string) => void;
};

type BookSearchInput = {
  word: string;
};

export default function BookSearchInput(props: BookSearchInputProps) {
  const { onSubmit, isLoading, word } = props;
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<BookSearchInput>({ defaultValues: { word: word } });

  const handlePreSubmit = (item: BookSearchInput) => {
    if (!onSubmit || !item) {
      return;
    }
    onSubmit(item.word);
  };

  return (
    <>
      <form onSubmit={handleSubmit(handlePreSubmit)}>
        <Grid
          container
          spacing={1}
          sx={{
            justifyContent: "center",
            alignItems: "stretch",
            mx: 1,
            my: 1,
          }}
        >
          <Grid size={{ xs: 12, md: 5 }}>
            <TextField
              fullWidth
              {...register("word", {
                required: { value: true, message: "入力が必要です。" },
              })}
              error={Boolean(errors.word)}
              helperText={errors.word && errors.word.message}
              slotProps={{
                input: {
                  startAdornment: (
                    <InputAdornment position="start">
                      <SearchIcon />
                    </InputAdornment>
                  ),
                },
              }}
              variant="standard"
            />
          </Grid>
          <Grid size={{ xs: 12, md: 2 }}>
            <Button
              variant="outlined"
              onClick={handleSubmit(handlePreSubmit)}
              disabled={isLoading}
            >
              検索
            </Button>
          </Grid>
        </Grid>
      </form>
    </>
  );
}
