import { SVGProps } from "react";
export const DeleteSvg = (props: SVGProps<SVGSVGElement>) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width={10}
    height={10}
    fill="none"
    {...props}
  >
    <g stroke="#000" strokeLinecap="round">
      <path d="m1 1 8 8M1 9l8-8" />
    </g>
  </svg>
);
