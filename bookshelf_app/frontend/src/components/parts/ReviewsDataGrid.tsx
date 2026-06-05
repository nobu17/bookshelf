import {
  DataGrid,
  GridColDef,
  GridRenderCellParams,
} from "@mui/x-data-grid";
import EditIcon from "@mui/icons-material/Edit";
import DeleteIcon from "@mui/icons-material/Delete";

import { dateToString } from "../../libs/utils/date";
import { Review, toJapanese } from "../../types/data";
import DataGridActionIconButton from "./DataGridActionIconButton";
import { readonlyDataGridProps } from "../../libs/utils/dataGrid";

type ReviewsDataGridProps = {
  reviews: Review[];
  onEdit?: (review: Review) => void;
  onDelete?: (review: Review) => void;
};

type ReviewGridRow = Review & {
  enabled?: boolean;
};

export default function ReviewsDataGrid(props: ReviewsDataGridProps) {
  const { reviews, onEdit, onDelete } = props;
  const columns: GridColDef[] = [
    {
      field: "completedAt",
      headerName: "読了日",
      width: 120,
      valueGetter: (_, row) =>
        `${row.completedAt ? dateToString(row.completedAt) : "--"}`,
    },
    {
      field: "state",
      headerName: "状態",
      width: 100,
      valueGetter: (_, row) => `${toJapanese(row.state)}`,
    },
    {
      field: "isDraft",
      headerName: "下書き",
      width: 80,
      valueGetter: (_, row) => `${row.isDraft ? "◯" : ""}`,
    },
    {
      field: "id",
      width: 100,
      headerName: "",
      sortable: false,
      renderCell: (params: GridRenderCellParams) => {
        return (
          <>
            <DataGridActionIconButton
              label="編集"
              color="primary"
              icon={EditIcon}
              onClick={() => handleEdit(params.row)}
            />
            <DataGridActionIconButton
              label="削除"
              color="error"
              icon={DeleteIcon}
              onClick={() => handleDelete(params.row)}
            />
          </>
        );
      },
    },
  ];
  const handleEdit = (review: Review) => {
    if (!review || !onEdit) {
      return;
    }
    onEdit(review);
  };

  const handleDelete = (review: Review) => {
    if (!review || !onDelete) {
      return;
    }
    onDelete(review);
  };

  return (
    <>
      <div style={{ maxHeight: 400 }}>
        <DataGrid<ReviewGridRow>
          {...readonlyDataGridProps}
          rows={reviews}
          columns={columns}
          editMode="row"
          hideFooter
          getRowClassName={(params) =>
            `table-row-enabled--${params.row.enabled}`
          }
          getRowId={(row: ReviewGridRow) => row.reviewId}
        />
      </div>
    </>
  );
}
