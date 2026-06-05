import { IconButton, Tooltip } from "@mui/material";
import { SvgIconComponent } from "@mui/icons-material";

type DataGridActionIconButtonProps = {
  label: string;
  color: "primary" | "error";
  icon: SvgIconComponent;
  onClick: () => void;
};

export default function DataGridActionIconButton(
  props: DataGridActionIconButtonProps
) {
  const { label, color, icon: Icon, onClick } = props;

  return (
    <Tooltip title={label}>
      <IconButton aria-label={label} color={color} onClick={onClick}>
        <Icon />
      </IconButton>
    </Tooltip>
  );
}
