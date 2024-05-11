import { TreeNode } from "@/components/base/tree-node-list";
import { INDENT_REM } from "@/const/const";
import { Button } from "../button";
import { EditSvg } from "@/data/image/edit-svg";
import { DeleteSvg } from "@/data/image/delete-svg";

type NodeItemProps = {
  depth: number;
  node: TreeNode;
  parentId: string;
  isDragStarted: boolean;
  handleDelete: (e: React.MouseEvent<HTMLButtonElement>) => void;
  handleDragEnd: (e: React.DragEvent<HTMLDivElement>) => void;
  handleDragEnter: (e: React.DragEvent<HTMLDivElement>) => void;
  handleDragLeave: (e: React.DragEvent<HTMLDivElement>) => void;
  handleDragOver: (e: React.DragEvent<HTMLDivElement>) => void;
  handleDragStart: (e: React.DragEvent<HTMLDivElement>) => void;
  handleDrop: (e: React.DragEvent<HTMLDivElement>) => void;
  handleToggleCheck: (e: React.MouseEvent<HTMLInputElement>) => void;
  handleToggleOpen: (e: React.MouseEvent<HTMLElement>) => void;
};

export const NodeItem = (props: NodeItemProps) => {
  const {
    depth,
    node,
    parentId,
    isDragStarted,
    handleToggleCheck,
    handleDelete,
    handleDragEnd,
    handleDragEnter,
    handleDragLeave,
    handleDragOver,
    handleDragStart,
    handleDrop,
    handleToggleOpen,
  } = props;

  return (
    <div className="flex flex-row focus:bg-red-300">
      <div style={{ width: `${depth * INDENT_REM}rem` }} />
      <div
        className="flex h-8 flex-1 flex-row border border-solid border-gray-300"
        draggable
        onDragEnd={handleDragEnd}
        onDragEnter={handleDragEnter}
        onDragLeave={handleDragLeave}
        onDragOver={handleDragOver}
        onDragStart={handleDragStart}
        onDrop={handleDrop}
        data-drop-target-type={"node"}
        data-node-id={node.id}
        data-parent-id={parentId}
      >
        <div
          className={`flex flex-1 flex-row ${
            isDragStarted ? "pointer-events-none" : ""
          }`}
        >
          {node.children.length !== 0 && (
            <div className="flex flex-col text-gray-600">
              <button
                className={`h-8 w-8 border-none bg-transparent text-gray-600 ${
                  node.isOpen ? "rotate-90" : ""
                }`}
                onClick={handleToggleOpen}
                data-node-id={node.id}
              >
                ▶︎
              </button>
            </div>
          )}
          <div className="flex w-8 flex-col">
            <input
              className="m-auto"
              type="checkbox"
              checked={node.isCompleted}
              onClick={handleToggleCheck}
              data-node-id={node.id}
            />
          </div>
          <div className="flex flex-1 flex-col">
            <span className="my-auto">{node.name}</span>
          </div>
          <div className="mr-2 flex space-x-2">
            <Button
              data-node-id={node.id}
              className="m-auto size-6 rounded-none border bg-white p-0 hover:bg-white hover:opacity-70"
            >
              <EditSvg />
            </Button>
            <Button
              onClick={handleDelete}
              data-node-id={node.id}
              className="m-auto size-6 rounded-none border bg-white p-0 hover:bg-white hover:opacity-70"
            >
              <DeleteSvg />
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};
