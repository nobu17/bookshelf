import * as React from "react";
import { Link } from "react-router-dom";
import AppBar from "@mui/material/AppBar";
import Box from "@mui/material/Box";
import Toolbar from "@mui/material/Toolbar";
import IconButton from "@mui/material/IconButton";
import Typography from "@mui/material/Typography";
import Menu from "@mui/material/Menu";
import MenuIcon from "@mui/icons-material/Menu";
import Container from "@mui/material/Container";
import Button from "@mui/material/Button";
import MenuItem from "@mui/material/MenuItem";
import { AccountCircle } from "@mui/icons-material";
import AutoStoriesIcon from "@mui/icons-material/AutoStories";

type ResponsiveAppBarProps = {
  title: string;
  menus: PageLink[];
  userMenus: PageLink[];
  isAuthorized: boolean;
  onMenuSelect: (menu: PageLink) => void;
};

type PageLink = {
  name: string;
  link: string;
};

export default function ResponsiveAppBar(props: ResponsiveAppBarProps) {
  const { title, menus, userMenus, isAuthorized, onMenuSelect } = props;
  const [anchorElNav, setAnchorElNav] = React.useState<null | HTMLElement>(
    null
  );
  const [anchorElUserNav, setAnchorElUserNav] =
    React.useState<null | HTMLElement>(null);
  const handleOpenNavMenu = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorElNav(event.currentTarget);
  };
  const handleCloseNavMenu = () => {
    setAnchorElNav(null);
  };
  const handleOpenUserNavMenu = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorElUserNav(event.currentTarget);
  };
  const handleCloseUserNavMenu = () => {
    setAnchorElUserNav(null);
  };
  const handleLinkClick = (menu: PageLink) => {
    setAnchorElNav(null);
    setAnchorElUserNav(null);
    onMenuSelect(menu);
  };

  const brand = (
    <>
      <AutoStoriesIcon sx={{ mr: 1 }} />
      <Typography
        noWrap
        component="span"
        sx={{
          fontWeight: 700,
          color: "inherit",
          textDecoration: "none",
          lineHeight: 1,
        }}
      >
        {title}
      </Typography>
    </>
  );

  return (
    <AppBar position="sticky" sx={{ mb: 2 }}>
      <Container maxWidth="xl">
        <Toolbar disableGutters>
          <Box
            component={Link}
            to="/"
            sx={{
              mr: 2,
              display: { xs: "none", md: "flex" },
              alignItems: "center",
              color: "inherit",
              textDecoration: "none",
            }}
          >
            {brand}
          </Box>

          <Box sx={{ flexGrow: 1, display: { xs: "flex", md: "none" } }}>
            <IconButton
              size="large"
              aria-label="account of current user"
              aria-controls="menu-appbar"
              aria-haspopup="true"
              onClick={handleOpenNavMenu}
              color="inherit"
            >
              <MenuIcon />
            </IconButton>
            <Menu
              id="menu-appbar"
              anchorEl={anchorElNav}
              anchorOrigin={{
                vertical: "bottom",
                horizontal: "left",
              }}
              keepMounted
              transformOrigin={{
                vertical: "top",
                horizontal: "left",
              }}
              open={Boolean(anchorElNav)}
              onClose={handleCloseNavMenu}
              sx={{ display: { xs: "block", md: "none" } }}
            >
              {menus.map((menu) => (
                <MenuItem key={menu.name} onClick={() => handleLinkClick(menu)}>
                  <Typography sx={{ textAlign: "center" }}>
                    {menu.name}
                  </Typography>
                </MenuItem>
              ))}
            </Menu>
          </Box>
          <Box
            component={Link}
            to="/"
            sx={{
              mr: 2,
              display: { xs: "flex", md: "none" },
              alignItems: "center",
              flexGrow: 1,
              color: "inherit",
              textDecoration: "none",
            }}
          >
            {brand}
          </Box>
          <Box sx={{ flexGrow: 1, display: { xs: "none", md: "flex" } }}>
            {menus.map((menu) => (
              <Button
                key={menu.name}
                onClick={() => handleLinkClick(menu)}
                sx={{ my: 2, color: "white", display: "block" }}
              >
                {menu.name}
              </Button>
            ))}
          </Box>
          {isAuthorized && (
            <div>
              <IconButton
                size="large"
                aria-label="account of current user"
                aria-controls="menu-appbar"
                aria-haspopup="true"
                onClick={handleOpenUserNavMenu}
                color="inherit"
              >
                <AccountCircle />
              </IconButton>
              <Menu
                id="menu-appbar"
                anchorEl={anchorElUserNav}
                anchorOrigin={{
                  vertical: "top",
                  horizontal: "right",
                }}
                keepMounted
                transformOrigin={{
                  vertical: "top",
                  horizontal: "right",
                }}
                open={Boolean(anchorElUserNav)}
                onClose={handleCloseUserNavMenu}
              >
                {userMenus.map((menu) => (
                  <MenuItem
                    key={menu.name}
                    onClick={() => handleLinkClick(menu)}
                  >
                    <Typography sx={{ textAlign: "center" }}>
                      {menu.name}
                    </Typography>
                  </MenuItem>
                ))}
              </Menu>
            </div>
          )}
        </Toolbar>
      </Container>
    </AppBar>
  );
}
