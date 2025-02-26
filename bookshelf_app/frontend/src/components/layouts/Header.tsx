import { useNavigate } from "react-router-dom";

import ResponsiveAppBar from "../parts/ResponsiveAppBar";
import { useAuth } from "../contexts/AuthContext";

const title = "技術書感想";
const menus = [{ name: "ホーム", link: "/" }];
const userMenus = [
  { name: "マイページ", link: "/mypage" },
  { name: "ログアウト", link: "/auth/signout" },
];

function Header() {
  const navigate = useNavigate();
  const { state } = useAuth();
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
        userMenus={userMenus}
        isAuthorized={state.isAuthorized}
        onMenuSelect={handleMenuClick}
      ></ResponsiveAppBar>
    </>
  );
}

export default Header;
