import { Route, Routes, BrowserRouter } from "react-router-dom";
import {
  createTheme,
  responsiveFontSizes,
  ThemeProvider,
} from "@mui/material/styles";
import Container from "@mui/material/Container";

import Header from "./components/layouts/Header";
import Home from "./pages/home/Home";
import UserReviews from "./pages/reviews/UserReviews";

import GlobalSpinner from "./components/containers/GlobalSpinner";
import GlobalSpinnerContextProvider from "./components/contexts/GlobalSpinnerContext";

import "./App.css";
import SignIn from "./pages/auth/SignIn";
import { AuthContextProvider } from "./components/contexts/AuthContext";
import MyHome from "./pages/mypage/MyHome";
import SignOut from "./pages/auth/SignOut";

let theme = createTheme({
  typography: {
    fontFamily: ["M PLUS Rounded 1c"].join(","),
  },
  palette: {
    mode: "light",
    // primary: {
    //   light: "#5f5fc4",
    //   main: "#283593",
    //   dark: "#001064",
    //   contrastText: "#ffffff",
    // },
  },
});
theme = responsiveFontSizes(theme);

function App() {
  return (
    <>
      <ThemeProvider theme={theme}>
        <AuthContextProvider>
          <GlobalSpinnerContextProvider>
            <BrowserRouter>
              <GlobalSpinner />
              <Header></Header>
              <Container maxWidth="lg" disableGutters>
                <Routes>
                  <Route path="/auth/signin" element={<SignIn />} />
                  <Route path="/auth/signout" element={<SignOut />} />
                  <Route path="/mypage" element={<MyHome />} />
                  <Route path="/reviews/user/:id" element={<UserReviews />} />
                  <Route path="*" element={<Home />} />
                </Routes>
              </Container>
            </BrowserRouter>
          </GlobalSpinnerContextProvider>
        </AuthContextProvider>
      </ThemeProvider>
    </>
  );
}

export default App;
