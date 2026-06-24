import { useState } from "react";
import {
  Alert,
  Button,
  Card,
  CardActions,
  CardContent,
  CircularProgress,
  Stack,
  Typography,
} from "@mui/material";
import DeleteSweepIcon from "@mui/icons-material/DeleteSweep";

import DebugApi from "../../libs/apis/debug";
import useAuthApi from "../../hooks/UseAuthApi";
import { useConfirmDialog } from "../../hooks/dialogs/UseConfirmDialog";
import { toError } from "../../libs/utils/error";
import ErrorAlert from "../parts/ErrorAlert";

const debugApi = new DebugApi();

type Message = {
  severity: "success" | "info";
  text: string;
};

export default function AdminDebugContainer() {
  useAuthApi(debugApi);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const [message, setMessage] = useState<Message | null>(null);
  const { showConfirmDialog, renderConfirmDialog } = useConfirmDialog();

  const clearPublisherCatalogCache = async () => {
    const confirmed = await showConfirmDialog(
      "確認",
      "出版社カタログキャッシュを削除します。次回の出版社検索時に公式カタログを再取得します。よろしいですか？"
    );
    if (!confirmed) {
      return;
    }
    await clearCache(async () => {
      const res = await debugApi.clearPublisherCatalogCache();
      return `出版社カタログキャッシュを ${res.data.deletedCount} 件削除しました。`;
    });
  };

  const clearBookMetadataCache = async () => {
    const confirmed = await showConfirmDialog(
      "確認",
      "書籍メタデータキャッシュを削除します。次回の出版社検索時にopenBD / Google Booksで再補完します。よろしいですか？"
    );
    if (!confirmed) {
      return;
    }
    await clearCache(async () => {
      const res = await debugApi.clearBookMetadataCache();
      return `書籍メタデータキャッシュを ${res.data.deletedCount} 件削除しました。`;
    });
  };

  const clearCache = async (action: () => Promise<string>) => {
    setLoading(true);
    try {
      setError(null);
      setMessage(null);
      const text = await action();
      setMessage({ severity: "success", text });
    } catch (e: unknown) {
      setError(toError(e));
    } finally {
      setLoading(false);
    }
  };

  if (error) {
    return <ErrorAlert error={error} />;
  }

  return (
    <>
      <Stack spacing={2}>
        {message ? <Alert severity={message.severity}>{message.text}</Alert> : <></>}
        {loading ? <CircularProgress /> : <></>}
        <CacheCard
          title="出版社カタログキャッシュ"
          description="出版社公式ページから取得したISBN、タイトル、発行日などの一覧です。削除すると次回の出版社検索で公式カタログを再取得します。"
          buttonText="出版社カタログを削除"
          disabled={loading}
          onClick={clearPublisherCatalogCache}
        />
        <CacheCard
          title="書籍メタデータキャッシュ"
          description="ISBNごとにopenBD / Google Booksで補完した著者、出版社、書影、概要などです。削除すると次回の出版社検索で再補完します。"
          buttonText="書籍メタデータを削除"
          disabled={loading}
          onClick={clearBookMetadataCache}
        />
      </Stack>
      {renderConfirmDialog()}
    </>
  );
}

type CacheCardProps = {
  title: string;
  description: string;
  buttonText: string;
  disabled: boolean;
  onClick: () => void;
};

function CacheCard(props: CacheCardProps) {
  return (
    <Card variant="outlined" sx={{ borderRadius: 1 }}>
      <CardContent>
        <Typography variant="h6">{props.title}</Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
          {props.description}
        </Typography>
      </CardContent>
      <CardActions sx={{ px: 2, pb: 2 }}>
        <Button
          variant="outlined"
          color="error"
          startIcon={<DeleteSweepIcon />}
          disabled={props.disabled}
          onClick={props.onClick}
        >
          {props.buttonText}
        </Button>
      </CardActions>
    </Card>
  );
}
