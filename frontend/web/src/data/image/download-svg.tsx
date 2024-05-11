import { SVGProps } from "react";
export const DownloadSvg = (props: SVGProps<SVGSVGElement>) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width={32}
    height={32}
    fill="none"
    {...props}
  >
    <path
      fill="#fff"
      d="m15.667 18.667-.707.707.707.707.707-.707-.707-.707Zm1-12a1 1 0 1 0-2 0h2Zm-8.374 6.04 6.667 6.667 1.414-1.414-6.667-6.667-1.414 1.414Zm8.08 6.667 6.667-6.667-1.414-1.414-6.666 6.667 1.414 1.414Zm.294-.707v-12h-2v12h2Z"
    />
    <path
      stroke="#fff"
      strokeWidth={2}
      d="M7 21.333v1.334a2.667 2.667 0 0 0 2.667 2.666H23a2.667 2.667 0 0 0 2.667-2.666v-1.334"
    />
  </svg>
);
