import { DataGrid, GridColDef, GridRenderCellParams } from "@mui/x-data-grid";
import { Box, Link, Tooltip, Typography } from "@mui/material";
import EditIcon from "@mui/icons-material/Edit";

import { BookMasterInfo } from "../../types/data";
import { dateToString } from "../../libs/utils/date";
import { getBookInfoImageUrl, getFallbackImageUrl } from "../../libs/utils/image";
import DataGridActionIconButton from "./DataGridActionIconButton";
import { readonlyDataGridProps } from "../../libs/utils/dataGrid";

type BookMasterDataGridProps = {
  books: BookMasterInfo[];
  onEdit: (book: BookMasterInfo) => void;
};

export default function BookMasterDataGrid(props: BookMasterDataGridProps) {
  const { books, onEdit } = props;
  const columns: GridColDef[] = [
    {
      field: "actions",
      headerName: "",
      width: 72,
      sortable: false,
      renderCell: (params: GridRenderCellParams<BookMasterInfo>) => (
        <DataGridActionIconButton
          label="編集"
          color="primary"
          icon={EditIcon}
          onClick={() => onEdit(params.row)}
        />
      ),
    },
    {
      field: "imageUrl",
      headerName: "書影",
      width: 90,
      sortable: false,
      renderCell: (params: GridRenderCellParams<BookMasterInfo>) => (
        <Box
          component="img"
          sx={{ width: 48, height: 72, objectFit: "contain", mt: 1 }}
          src={getBookInfoImageUrl(params.row)}
          onError={(e) => {
            e.currentTarget.src = getFallbackImageUrl();
          }}
        />
      ),
    },
    {
      field: "title",
      headerName: "書籍名",
      width: 280,
      renderCell: (params: GridRenderCellParams<BookMasterInfo>) => (
        <Tooltip title={params.row.title}>
          <Link
            component="button"
            underline="hover"
            onClick={() => onEdit(params.row)}
            sx={{
              display: "block",
              maxWidth: "100%",
              overflow: "hidden",
              textAlign: "left",
              textOverflow: "ellipsis",
              whiteSpace: "nowrap",
            }}
          >
            {params.row.title}
          </Link>
        </Tooltip>
      ),
    },
    {
      field: "tags",
      headerName: "タグ",
      width: 240,
      renderCell: (params: GridRenderCellParams<BookMasterInfo>) => {
        const tagNames = params.row.tags.map((tag) => tag.name).join(", ");
        return (
          <Tooltip title={tagNames}>
            <Typography
              sx={{
                overflow: "hidden",
                textOverflow: "ellipsis",
                whiteSpace: "nowrap",
              }}
            >
              {tagNames}
            </Typography>
          </Tooltip>
        );
      },
    },
    {
      field: "publishedAt",
      headerName: "出版日",
      width: 120,
      valueGetter: (_, row) => dateToString(row.publishedAt),
    },
    {
      field: "reviewCount",
      headerName: "レビュー数",
      width: 100,
      valueGetter: (_, row) => `${row.reviewCount}`,
    },
  ];

  return (
    <div style={{ height: 640 }}>
      <DataGrid
        {...readonlyDataGridProps}
        rows={books}
        columns={columns}
        getRowId={(row) => row.bookId}
        rowHeight={88}
      />
    </div>
  );
}
