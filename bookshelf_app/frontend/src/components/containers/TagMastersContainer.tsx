import { useEffect, useMemo, useState } from "react";
import {
  Button,
  CircularProgress,
  Stack,
  TextField,
  Tooltip,
} from "@mui/material";
import AddIcon from "@mui/icons-material/Add";
import ClearIcon from "@mui/icons-material/Clear";

import TagsApi from "../../libs/apis/tags";
import useAuthApi from "../../hooks/UseAuthApi";
import { BookTag } from "../../types/data";
import ErrorAlert from "../parts/ErrorAlert";
import TagMasterDataGrid from "../parts/TagMasterDataGrid";
import TagMasterEditDialog from "../parts/dialogs/TagMasterEditDialog";
import { useConfirmDialog } from "../../hooks/dialogs/UseConfirmDialog";
import { normalizeBookTagName } from "../../libs/services/bookTags";
import { toError } from "../../libs/utils/error";

const tagsApi = new TagsApi();

type DialogState = {
  open: boolean;
  tag: BookTag | null;
};

const initialDialogState: DialogState = {
  open: false,
  tag: null,
};

export default function TagMastersContainer() {
  useAuthApi(tagsApi);
  const [keyword, setKeyword] = useState("");
  const [tags, setTags] = useState<BookTag[]>([]);
  const [dialogState, setDialogState] =
    useState<DialogState>(initialDialogState);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const { showConfirmDialog, renderConfirmDialog } = useConfirmDialog();
  const displayedTags = useMemo(() => {
    return filterTags(tags, keyword).sort((a, b) =>
      a.name.localeCompare(b.name, "ja")
    );
  }, [tags, keyword]);

  useEffect(() => {
    loadAsync();
  }, []);

  const loadAsync = async () => {
    setLoading(true);
    try {
      const res = await tagsApi.list();
      setTags(res.data.tags);
      setError(null);
    } catch (e: unknown) {
      setError(toError(e));
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = () => {
    setDialogState({ open: true, tag: null });
  };
  const handleEdit = (tag: BookTag) => {
    setDialogState({ open: true, tag });
  };
  const handleCloseDialog = () => {
    setDialogState(initialDialogState);
  };
  const handleSubmit = async (name: string) => {
    setLoading(true);
    try {
      if (dialogState.tag) {
        await tagsApi.update(dialogState.tag.id, name);
      } else {
        await tagsApi.create(name);
      }
      setDialogState(initialDialogState);
      await loadAsync();
    } catch (e: unknown) {
      setError(toError(e));
    } finally {
      setLoading(false);
    }
  };
  const handleDelete = async (tag: BookTag) => {
    const confirmed = await showConfirmDialog(
      "確認",
      `タグ「${tag.name}」を削除します。使用中の本からも表示されなくなる可能性があります。よろしいですか？`
    );
    if (!confirmed) {
      return;
    }
    setLoading(true);
    try {
      await tagsApi.delete(tag.id);
      await loadAsync();
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
      <Stack direction={{ xs: "column", sm: "row" }} spacing={2} sx={{ mb: 2 }}>
        <TextField
          label="キーワード"
          placeholder="タグ名で検索"
          value={keyword}
          onChange={(event) => setKeyword(event.target.value)}
          fullWidth
        />
        {keyword ? (
          <Tooltip title="検索条件をクリア">
            <Button
              aria-label="clear"
              variant="outlined"
              onClick={() => setKeyword("")}
              sx={{ minWidth: 56, px: 2 }}
            >
              <ClearIcon />
            </Button>
          </Tooltip>
        ) : (
          <></>
        )}
        <Tooltip title="新規作成">
          <Button
            aria-label="create"
            variant="contained"
            onClick={handleCreate}
            sx={{ minWidth: 56, px: 2 }}
          >
            <AddIcon />
          </Button>
        </Tooltip>
      </Stack>
      {loading ? (
        <CircularProgress />
      ) : (
        <TagMasterDataGrid
          tags={displayedTags}
          onEdit={handleEdit}
          onDelete={handleDelete}
        />
      )}
      <TagMasterEditDialog
        open={dialogState.open}
        tag={dialogState.tag}
        onSubmit={handleSubmit}
        onClose={handleCloseDialog}
      />
      {renderConfirmDialog()}
    </>
  );
}

const filterTags = (tags: BookTag[], keyword: string): BookTag[] => {
  const normalizedKeyword = normalizeSearchText(keyword);
  if (!normalizedKeyword) {
    return tags;
  }
  return tags.filter((tag) =>
    normalizeSearchText(tag.name).includes(normalizedKeyword)
  );
};

const normalizeSearchText = (value: string): string => {
  return normalizeBookTagName(value).normalize("NFKC").toLocaleLowerCase();
};
