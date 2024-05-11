export const INDENT_REM: number = 2;
export const SERVER_BASE_URL: string =
  process.env.NEXT_PUBLIC_SERVER_ADDRESS && process.env.NEXT_PUBLIC_SERVER_PORT
    ? `${process.env.NEXT_PUBLIC_SERVER_ADDRESS}:${process.env.NEXT_PUBLIC_SERVER_PORT}`
    : "http://localhost:5000";
