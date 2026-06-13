import { DataGrid, GridColDef, GridRenderCellParams } from "@mui/x-data-grid";
import { Box, Link, Tooltip } from "@mui/material";
import DeleteIcon from "@mui/icons-material/Delete";
import EditIcon from "@mui/icons-material/Edit";

import { BookTag } from "../../types/data";
import DataGridActionIconButton from "./DataGridActionIconButton";
import { readonlyDataGridProps } from "../../libs/utils/dataGrid";

type TagMasterDataGridProps = {
  tags: BookTag[];
  onEdit: (tag: BookTag) => void;
  onDelete: (tag: BookTag) => void;
};

export default function TagMasterDataGrid(props: TagMasterDataGridProps) {
  const { tags, onEdit, onDelete } = props;
  const columns: GridColDef[] = [
    {
      field: "actions",
      headerName: "",
      width: 112,
      sortable: false,
      renderCell: (params: GridRenderCellParams<BookTag>) => (
        <>
          <DataGridActionIconButton
            label="編集"
            color="primary"
            icon={EditIcon}
            onClick={() => onEdit(params.row)}
          />
          <DataGridActionIconButton
            label="削除"
            color="error"
            icon={DeleteIcon}
            onClick={() => onDelete(params.row)}
          />
        </>
      ),
    },
    {
      field: "name",
      headerName: "タグ名",
      flex: 1,
      minWidth: 240,
      renderCell: (params: GridRenderCellParams<BookTag>) => (
        <Tooltip title={params.row.name}>
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
            {params.row.name}
          </Link>
        </Tooltip>
      ),
    },
  ];

  return (
    <Box sx={{ height: 640 }}>
      <DataGrid
        {...readonlyDataGridProps}
        rows={tags}
        columns={columns}
        getRowId={(row) => row.id}
      />
    </Box>
  );
}
