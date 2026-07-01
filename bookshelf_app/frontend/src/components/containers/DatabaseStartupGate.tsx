import { useEffect, useMemo, useState } from "react";
import RefreshIcon from "@mui/icons-material/Refresh";
import {
  Alert,
  Box,
  Button,
  CircularProgress,
  Container,
  Typography,
} from "@mui/material";

import BookWithReviewsApi from "../../libs/apis/bookWithReviews";
import HealthApi from "../../libs/apis/health";
import { BookWithReviews } from "../../types/data";
import BookCards from "../parts/BookCards";

type DatabaseStatus = "starting" | "ready" | "error";

type DatabaseStartupGateProps = {
  children: React.ReactNode;
};

let databaseReadyPromise: Promise<void> | null = null;

const waitForDatabase = (): Promise<void> => {
  if (!databaseReadyPromise) {
    databaseReadyPromise = new HealthApi().waitForDatabase().catch((error) => {
      databaseReadyPromise = null;
      throw error;
    });
  }
  return databaseReadyPromise;
};

export default function DatabaseStartupGate({
  children,
}: DatabaseStartupGateProps) {
  const [status, setStatus] = useState<DatabaseStatus>("starting");
  const cachedBooks = useMemo<BookWithReviews[]>(() => {
    return (
      new BookWithReviewsApi().getCachedLatest()?.data.books_with_reviews ?? []
    );
  }, []);

  const startDatabase = async () => {
    setStatus("starting");
    try {
      await waitForDatabase();
      setStatus("ready");
    } catch {
      setStatus("error");
    }
  };

  useEffect(() => {
    void startDatabase();
  }, []);

  if (status === "ready") {
    return <>{children}</>;
  }

  return (
    <Box sx={{ minHeight: "100vh", bgcolor: "background.default" }}>
      <Box
        component="header"
        sx={{
          borderBottom: 1,
          borderColor: "divider",
          bgcolor: "background.paper",
          py: 2,
        }}
      >
        <Container maxWidth="lg">
          <Typography component="h1" variant="h6">
            技術書ノート
          </Typography>
        </Container>
      </Box>
      <Container maxWidth="lg" sx={{ py: 3 }}>
        {status === "starting" ? (
          <Alert
            severity="info"
            icon={<CircularProgress color="inherit" size={22} />}
            sx={{ mb: 3, alignItems: "center" }}
          >
            データベースを起動しています。初回の表示にはしばらく時間がかかることがあります。
          </Alert>
        ) : (
          <Alert
            severity="error"
            action={
              <Button
                color="inherit"
                size="small"
                startIcon={<RefreshIcon />}
                onClick={() => void startDatabase()}
              >
                再試行
              </Button>
            }
            sx={{ mb: 3, alignItems: "center" }}
          >
            データベースを起動できませんでした。
          </Alert>
        )}
        {cachedBooks.length > 0 ? (
          <Box>
            <Typography component="h2" variant="h5" sx={{ mb: 0.5 }}>
              最近読んだ本
            </Typography>
            <Typography color="text.secondary" sx={{ mb: 2 }}>
              前回表示した内容
            </Typography>
            <BookCards
              books={cachedBooks}
              disabled
              onSelect={() => undefined}
            />
          </Box>
        ) : (
          <Box
            sx={{
              minHeight: 240,
              display: "grid",
              placeItems: "center",
            }}
          >
            <CircularProgress />
          </Box>
        )}
      </Container>
    </Box>
  );
}
