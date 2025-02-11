import { useNavigate } from "react-router-dom";

import ResponsiveAppBar from "../parts/ResponsiveAppBar";

const title = "技術書感想";
const menus = [{ name: "hoge", link: "/" }];

function Header() {
  const navigate = useNavigate();
  const handleMenuClick = ({ link }: { name: string; link: string }) => {
    if (link.startsWith("http")) {
      window.open(link);
    } else {
      navigate(link);
    }
  };
  return (
    <>
      <ResponsiveAppBar
        title={title}
        menus={menus}
        onMenuSelect={handleMenuClick}
      ></ResponsiveAppBar>
    </>
  );
}

export default Header;
