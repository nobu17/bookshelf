import { NavLink as RouterLink } from "react-router-dom";
import Breadcrumbs from "@mui/material/Breadcrumbs";
import Link from "@mui/material/Link";
import NavigateNextIcon from "@mui/icons-material/NavigateNext";
import { Typography } from "@mui/material";

type PageHeaderWithBreadCrumbProps = {
  currentTitle: string;
  links: PageLink[];
};

type PageLink = {
  title: string;
  url: string;
};

export default function PageHeaderWithBreadCrumb(props: PageHeaderWithBreadCrumbProps) {
  return (
    <>
      <Breadcrumbs
        separator={<NavigateNextIcon fontSize="small" />}
        aria-label="breadcrumb"
        sx={{ mb: 2 }}
      >
        {props.links.map((item, index) => (
          <Link
            underline="hover"
            key={index}
            color="inherit"
            component={RouterLink}
            to={item.url}
          >
            {item.title}
          </Link>
        ))}
        <Typography color="text.primary">{props.currentTitle}</Typography>
      </Breadcrumbs>
    </>
  );
}