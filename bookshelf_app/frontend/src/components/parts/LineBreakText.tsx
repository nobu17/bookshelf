import React from "react";

type LineBreakTextProps = {
  text: string;
};

export default function LineBreakText(props: LineBreakTextProps) {
  const texts = props.text.split(/(\n)/).map((item, index) => {
    return (
      <React.Fragment key={index}>
        {item.match(/\n/) ? <br /> : item}
      </React.Fragment>
    );
  });
  return <>{texts}</>;
}