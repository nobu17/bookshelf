import Container from "@mui/material/Container";
import PageHeaderWithBreadCrumb from "../../components/parts/PageHeaderWithBreadCrumb";
import PageTitle from "../../components/parts/PageTitle";

type MyPageBaseProps = {
  title: string;
  links?: PageLink[];
  children?: JSX.Element;
};

type PageLink = {
  title: string;
  url: string;
};

const defaultLinks = [{ title: "マイページ", url: "/mypage" }];

export default function MyPageBase(props: MyPageBaseProps) {
  const link = props.links ? props.links : defaultLinks;
  return (
    <Container>
      <PageHeaderWithBreadCrumb currentTitle={props.title} links={link} />
      <PageTitle title={props.title} />
      {props.children}
    </Container>
  );
}
