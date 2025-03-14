import {
  DataGrid,
  GridColDef,
  GridRenderCellParams,
  GridRowParams,
} from "@mui/x-data-grid";
import { IconButton } from "@mui/material";
import EditIcon from "@mui/icons-material/Edit";
import DeleteIcon from "@mui/icons-material/Delete";

import { dateToString } from "../../libs/utils/date";
import { Review, toJapanese } from "../../types/data";

type ReviewsDataGridProps = {
  reviews: Review[];
  onEdit?: (review: Review) => void;
  onDelete?: (review: Review) => void;
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
            <IconButton
              aria-label="edit"
              color="primary"
              onClick={() => handleEdit(params.row)}
            >
              <EditIcon />
            </IconButton>
            <IconButton
              aria-label="delete"
              color="error"
              onClick={() => handleDelete(params.row)}
            >
              <DeleteIcon />
            </IconButton>
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
        <DataGrid
          // eslint-disable-next-line @typescript-eslint/no-unused-vars
          isRowSelectable={(_: GridRowParams) => false}
          rows={reviews}
          columns={columns}
          disableColumnFilter={true}
          disableColumnMenu={true}
          disableColumnSelector={true}
          disableDensitySelector={true}
          editMode="row"
          hideFooter
          getRowClassName={(params) =>
            `table-row-enabled--${params.row.enabled}`
          }
          // eslint-disable-next-line @typescript-eslint/no-explicit-any
          getRowId={(row: any) => row.reviewId}
        />
      </div>
    </>
  );
}
