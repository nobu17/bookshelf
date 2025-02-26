import PageTitle from "../../components/parts/PageTitle";
import { useAuthGuard } from "../../hooks/auth/UseAuthGuard";
import MyHomeContainer from "../../components/containers/MyHomeContainers";

function MyHome() {
  useAuthGuard();
  return (
    <>
      <PageTitle title="マイページ" />
      <MyHomeContainer />
    </>
  );
}

export default MyHome;
