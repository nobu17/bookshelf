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
        <GlobalSpinnerContextProvider>
          <BrowserRouter>
            <GlobalSpinner />
            <Header></Header>
            <Container maxWidth="lg" disableGutters>
              <Routes>
                <Route path="/reviews/user/:id" element={<UserReviews />} />
                <Route path="*" element={<Home />} />
              </Routes>
            </Container>
          </BrowserRouter>
        </GlobalSpinnerContextProvider>
      </ThemeProvider>
    </>
  );
}

export default App;
