import * as React from "react";
import {
  Button,
  Container,
  IconButton,
  InputAdornment,
  Stack,
  TextField,
} from "@mui/material";
import { Visibility, VisibilityOff } from "@mui/icons-material";

import { SubmitHandler, useForm } from "react-hook-form";
import { isValidEmail } from "../../libs/utils/email";

type LoginFormProps = {
  input: LoginInput;
  onSubmit: callbackSubmit;
  isLoading?: boolean;
};

type LoginInput = {
  email: string;
  password: string;
};

interface callbackSubmit {
  (item: LoginInput): void;
}

const RequiredErrorMessage = "入力が必要です。";

export default function LoginForm(props: LoginFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginInput>({ defaultValues: props.input });
  const [showPassword, setShowPassword] = React.useState(false);

  const onSubmit: SubmitHandler<LoginInput> = (data) => {
    if (props.isLoading) return;
    props.onSubmit(data);
  };
  const handleEmailValidation = (email: string) => {
    const isValid = isValidEmail(email);
    if (!isValid) {
      return "正しい形式のメールアドレスを入力してください。";
    }
    return;
  };

  const handleClickShowPassword = () => {
    setShowPassword(!showPassword);
  };
  return (
    <>
      <Container maxWidth="sm" sx={{ pt: 5 }}>
        <Stack component="form" spacing={3} onSubmit={handleSubmit(onSubmit)}>
          <TextField
            label="ID"
            fullWidth
            disabled={props.isLoading}
            {...register("email", {
              required: { value: true, message: RequiredErrorMessage },
              validate: handleEmailValidation,
            })}
            error={Boolean(errors.email)}
            helperText={errors.email && errors.email.message}
          />
          <TextField
            label="Password"
            fullWidth
            disabled={props.isLoading}
            type={showPassword ? "text" : "password"}
            autoComplete="current-password"
            {...register("password", {
              required: { value: true, message: RequiredErrorMessage },
            })}
            InputProps={{
              endAdornment: (
                <InputAdornment position="end">
                  <IconButton
                    aria-label="toggle password visibility"
                    onClick={handleClickShowPassword}
                    onMouseDown={(e) => e.preventDefault()}
                    edge="end"
                    disabled={props.isLoading}
                  >
                    {showPassword ? <VisibilityOff /> : <Visibility />}
                  </IconButton>
                </InputAdornment>
              ),
            }}
            error={Boolean(errors.password)}
            helperText={errors.password && errors.password.message}
          />
          <Button
            color="primary"
            variant="contained"
            size="large"
            type="submit"
            disabled={props.isLoading}
          >
            ログイン
          </Button>
        </Stack>
      </Container>
    </>
  );
}
