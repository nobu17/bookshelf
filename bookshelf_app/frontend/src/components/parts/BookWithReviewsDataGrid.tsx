import {
  DataGrid,
  GridColDef,
  GridColumnVisibilityModel,
  GridRenderCellParams,
} from "@mui/x-data-grid";
import { Box, Link } from "@mui/material";
import EditIcon from "@mui/icons-material/Edit";
import DeleteIcon from "@mui/icons-material/Delete";

import { BookWithReviews, Review, toJapanese } from "../../types/data";
import { FilterStateSelect } from "./FilterStateSelect";
import { FilterCondition, FilterConditionDef } from "../../types/filter";
import useFilterReviews from "../../hooks/UseFilterReviews";
import { useEffect, useState } from "react";
import { dateToString } from "../../libs/utils/date";
import DataGridActionIconButton from "./DataGridActionIconButton";
import { readonlyDataGridProps } from "../../libs/utils/dataGrid";

type BookWithReviewsDataGridProps = {
  reviews: BookWithReviews[];
  onSelect?: (info: BookWithReviews) => void;
  onEdit?: (info: SpecificBookSelectInfo) => void;
  onDelete?: (info: SpecificBookSelectInfo) => void;
};

type SpecificBookSelectInfo = {
  bookId: string;
  review: Review;
};

type BookWithReviewsGridRow = BookWithReviews & {
  enabled?: boolean;
};

export default function BookWithReviewsDataGrid(
  props: BookWithReviewsDataGridProps
) {
  const { reviews, onSelect, onEdit, onDelete } = props;
  const { condition, setCondition, filtered } = useFilterReviews(reviews);
  const [columnVisibilityModel, setColumnVisibilityModel] =
    useState<GridColumnVisibilityModel>({
      completedAt: true,
    });
  const columns: GridColDef[] = [
    {
      field: "completedAt",
      headerName: "読了日",
      width: 120,
      valueGetter: (_, row) =>
        `${
          row.representative?.completedAt
            ? dateToString(row.representative.completedAt)
            : "--"
        }`,
    },
    {
      field: "title",
      headerName: "書籍名",
      width: 300,
      renderCell: (params: GridRenderCellParams) => {
        return (
          <>
            <Link onClick={() => handleSelect(params.row)} underline="hover">
              {params.row.title}
            </Link>
          </>
        );
      },
    },
    {
      field: "state",
      headerName: "状態",
      width: 100,
      valueGetter: (_, row) => `${toJapanese(row.representative.state)}`,
    },
    {
      field: "isDraft",
      headerName: "下書き",
      width: 80,
      valueGetter: (_, row) => `${row.representative.isDraft ? "◯" : ""}`,
    },
    {
      field: "reviewCount",
      headerName: "レビュー数",
      width: 100,
      valueGetter: (_, row) => `${row.filteredReviews.length}`,
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
              onClick={() =>
                handleEdit(params.row.bookId, params.row.representative)
              }
            />
            <DataGridActionIconButton
              label="削除"
              color="error"
              icon={DeleteIcon}
              onClick={() =>
                handleDelete(params.row.bookId, params.row.representative)
              }
            />
          </>
        );
      },
    },
  ];

  useEffect(() => {
    setColumnVisibilityModel({
      completedAt:
        condition === FilterConditionDef.All ||
        condition === FilterConditionDef.OnlyCompleted,
    });
  }, [condition]);

  const handleSelect = (info: BookWithReviews) => {
    if (!info || !onSelect) {
      return;
    }
    // notify before filtered
    const original = reviews.find((x) => x.bookId === info.bookId);
    if (original) {
      onSelect(original);
    }
  };

  const handleEdit = (bookId: string, review: Review) => {
    if (!bookId || !review || !onEdit) {
      return;
    }
    onEdit({ bookId: bookId, review: review });
  };

  const handleDelete = (bookId: string, review: Review) => {
    if (!bookId || !review || !onDelete) {
      return;
    }
    onDelete({ bookId: bookId, review: review });
  };

  const handleFilterStateChange = (condition: FilterCondition) => {
    setCondition(condition);
  };

  return (
    <>
      <Box sx={{ mb: 2 }}>
        <FilterStateSelect
          label="表示条件"
          value={condition}
          onSelectionChanged={handleFilterStateChange}
        ></FilterStateSelect>
      </Box>
      <div style={{ height: 600 }}>
        <DataGrid<BookWithReviewsGridRow>
          {...readonlyDataGridProps}
          rows={filtered?.filtered}
          columns={columns}
          editMode="row"
          hideFooter
          getRowClassName={(params) =>
            `table-row-enabled--${params.row.enabled}`
          }
          getRowId={(row: BookWithReviewsGridRow) => row.bookId}
          columnVisibilityModel={columnVisibilityModel}
          onColumnVisibilityModelChange={(newModel) =>
            setColumnVisibilityModel(newModel)
          }
        />
      </div>
    </>
  );
}

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
