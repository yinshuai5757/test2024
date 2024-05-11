import { SVGProps } from "react";
export const AddSvg = (props: SVGProps<SVGSVGElement>) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width={20}
    height={20}
    fill="none"
    {...props}
  >
    <path
      fill="nonzero"
      d="M11.429 11.429V20H8.57v-8.571H0V8.57h8.571V0h2.858v8.571H20v2.858h-8.571Z"
    />
  </svg>
);
