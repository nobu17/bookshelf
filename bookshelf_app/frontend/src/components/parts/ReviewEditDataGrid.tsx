import { DataGrid, GridColDef, GridRenderCellParams } from "@mui/x-data-grid";
import { IconButton } from "@mui/material";
import EditIcon from "@mui/icons-material/Edit";
import DeleteIcon from "@mui/icons-material/Delete";

import {
  BookInfo,
  BookWithReviews,
  Review,
  toJapanese,
} from "../../types/data";
import { dateToString } from "../../libs/utils/date";

type ReviewEditDataGridProps = {
  reviews: BookWithReviews[];
  onEdit?: (info: SpecificBookSelectInfo) => void;
  onDelete?: (info: SpecificBookSelectInfo) => void;
};

type SpecificBookSelectInfo = {
  bookId: string;
  review: Review;
};

type DataGridRow = {
  book: BookInfo;
  review: Review;
};

export default function ReviewEditDataGrid(props: ReviewEditDataGridProps) {
  const { reviews, onEdit, onDelete } = props;
  const rows = convertToDataGridRow(reviews);
  const columns: GridColDef[] = [
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
    {
      field: "title",
      headerName: "書籍名",
      width: 300,
      valueGetter: (_, row) => `${row.book.title}`,
    },
    {
      field: "state",
      headerName: "状態",
      width: 100,
      valueGetter: (_, row) => `${toJapanese(row.review.state)}`,
    },
    {
      field: "isDraft",
      headerName: "ドラフト",
      width: 130,
      valueGetter: (_, row) => `${row.review.isDraft ? "○" : ""}`,
    },
    {
      field: "completedAt",
      headerName: "読了日",
      width: 150,
      valueGetter: (_, row) =>
        `${row.review.completedAt ? dateToString(row.review.completedAt) : ""}`,
    },
  ];

  const handleEdit = (info: DataGridRow) => {
    if (!info || !onEdit) {
      return;
    }
    onEdit({ bookId: info.book.bookId, review: info.review });
  };

  const handleDelete = (info: DataGridRow) => {
    if (!info || !onDelete) {
      return;
    }
    onDelete({ bookId: info.book.bookId, review: info.review });
  };

  return (
    <>
      <div style={{ height: 600 }}>
        <DataGrid
          rows={rows}
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
          getRowId={(row: any) => row.review.reviewId}
        />
      </div>
    </>
  );
}

const convertToDataGridRow = (
  bookReviews: BookWithReviews[]
): DataGridRow[] => {
  const rows: DataGridRow[] = [];
  for (const bookReview of bookReviews) {
    for (const review of bookReview.reviews) {
      rows.push({ book: bookReview, review: review });
    }
  }
  // console.log(rows);
  return rows;
};

// const styles = {
//   grid: {
//     ".MuiDataGrid-toolbarContainer": {
//       borderBottom: "solid 1px rgba(224, 224, 224, 1)",
//     },
//     ".MuiDataGrid-row .MuiDataGrid-cell:not(:last-child)": {
//       borderRight: "solid 1px rgba(224, 224, 224, 1) !important",
//     },
//     // 列ヘッダに背景色を指定
//     ".MuiDataGrid-columnHeaders": {
//       backgroundColor: "#65b2c6",
//       color: "#fff",
//     },
//     // disabled row
//     "& .table-row-enabled--false": {
//       backgroundColor: "#696969",
//       color: "#fff",
//       "&:hover": {
//         backgroundColor: "#696969",
//         color: "#fff",
//       },
//     },
//   },
// };
