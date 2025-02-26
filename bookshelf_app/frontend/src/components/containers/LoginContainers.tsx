import ErrorAlert from "../parts/ErrorAlert";
import LoginForm from "../parts/LoginForm";
import { useGlobalSpinnerContext } from "../contexts/GlobalSpinnerContext";
import { AuthError, useAuth } from "../contexts/AuthContext";
import { useSignInGuard } from "../../hooks/auth/UseSignInGuard";

export default function LoginContainer() {
  useSignInGuard();
  const { setIsSpinnerOn } = useGlobalSpinnerContext();
  const { signIn, error } = useAuth();

  const displayError = (authError: AuthError) => {
    if (authError != null) {
      let err: Error;
      if (authError == "Normal") {
        err = new Error("認証に失敗しました。");
      } else {
        err = new Error(
          "想定外エラーが発生しました。お手数ですが時間を置いて、再度お試しください。"
        );
      }
      return <ErrorAlert error={err} />;
    }
    return <></>;
  };

  const handleSubmit = async ({
    email,
    password,
  }: {
    email: string;
    password: string;
  }) => {
    setIsSpinnerOn(true);
    await signIn(email, password);
    setIsSpinnerOn(false);
  };
  return (
    <>
      {displayError(error)}
      <LoginForm
        input={{ email: "", password: "" }}
        onSubmit={handleSubmit}
      ></LoginForm>
    </>
  );
}
