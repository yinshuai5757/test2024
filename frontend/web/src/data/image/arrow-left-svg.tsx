import { SVGProps } from "react";
export const ArrowLeftSvg = (props: SVGProps<SVGSVGElement>) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width={12}
    height={16}
    fill="none"
    {...props}
  >
    <path
      fill="#555"
      d="M10 1.88 3.82 8 10 14.12 8.097 16 0 8l8.097-8L10 1.88Z"
    />
  </svg>
);
