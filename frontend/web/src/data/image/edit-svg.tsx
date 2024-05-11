import { SVGProps } from "react";
export const EditSvg = (props: SVGProps<SVGSVGElement>) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width={10}
    height={10}
    fill="none"
    {...props}
  >
    <path
      fill="#555"
      d="M9.9 2.385 7.615.1a.34.34 0 0 0-.48 0L.88 6.353l.014.014-.022-.006-.855 3.193a.339.339 0 0 0 .465.414v.002l3.162-.848-.002-.007.004.005L9.9 2.866a.34.34 0 0 0 0-.481Zm-8.842 6.55.508-1.896 1.388 1.388-1.896.508Z"
    />
  </svg>
);
