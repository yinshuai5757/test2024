import Link from "next/link";

export const Header = () => {
  return (
    <header className="border-brand border-b-2 px-3 py-2">
      <div className="flex justify-between">
        <div className="flex items-center space-x-4">
          <h1 className="text-brand flex">
            <div>
              <p className="text-xs">準備書面作成支援ツール</p>
              <p className="text-xl font-bold">JS-copilot</p>
            </div>
          </h1>
          <div className="text-xs">
            <p>ベータ版</p>
            <p>ver 0.0.1</p>
          </div>
        </div>
        <nav className="flex items-end text-sm">
          <div className="flex items-center space-x-4">
            <Link className="" href="#">
              準備書面作成機能
            </Link>
            <span className="text-xs font-light">|</span>
            <Link className="text-disabled pointer-events-none" href="#">
              文献参照機能
            </Link>
            <span className="text-xs font-light">|</span>
            <Link className="" href="#">
              ヘルプ
            </Link>
          </div>
        </nav>
      </div>
    </header>
  );
};
