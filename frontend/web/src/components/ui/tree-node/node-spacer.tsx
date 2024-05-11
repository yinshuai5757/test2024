import { TreeNode } from "@/components/base/tree-node-list";
import { INDENT_REM } from "@/const/const";

type SpacerPosition = "first" | "last" | "theOthers";

type SpacerProps = {
  depth: number;
  node: TreeNode | null;
  parentId: string;
  position: SpacerPosition;
  isDragStarted: boolean;
  handleDragEnter: (e: React.DragEvent<HTMLDivElement>) => void;
  handleDragLeave: (e: React.DragEvent<HTMLDivElement>) => void;
  handleDragOver: (e: React.DragEvent<HTMLDivElement>) => void;
  handleDrop: (e: React.DragEvent<HTMLDivElement>) => void;
};

export const Spacer = (props: SpacerProps) => {
  const {
    depth,
    node,
    parentId,
    position,
    isDragStarted,
    handleDragEnter,
    handleDragLeave,
    handleDragOver,
    handleDrop,
  } = props;

  return (
    <div className="flex flex-row">
      <div style={{ width: `${depth * INDENT_REM}rem` }} />
      <div
        className="w-full flex-1 py-0.5"
        onDragEnter={handleDragEnter}
        onDragLeave={handleDragLeave}
        onDragOver={handleDragOver}
        onDrop={handleDrop}
        data-drop-target-type={"spacer"}
        data-first={position === "first" || null}
        data-last={position === "last" || null}
        data-next-id={node ? node.id : null}
        data-parent-id={parentId}
      >
        <div className={isDragStarted ? "pointer-events-none" : ""} />
      </div>
    </div>
  );
};
