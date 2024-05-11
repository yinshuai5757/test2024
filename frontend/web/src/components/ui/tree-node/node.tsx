import { ArboristNodeType } from "@/app/page";
import { Button } from "../button";
import { NodeRendererProps } from "react-arborist";
import { useState } from "react";
import { DeleteSvg } from "@/data/image/delete-svg";
import { EditSvg } from "@/data/image/edit-svg";

export const Node = ({
  node,
  style,
  dragHandle,
  tree,
  selectedNodeId,
  setSelectedNodeId,
  onSelect,
}: NodeRendererProps<ArboristNodeType> & {
  selectedNodeId: string;
  setSelectedNodeId: (id: string) => void;
  onSelect: (node: ArboristNodeType) => void;
}) => {
  const [composing, setComposing] = useState(false);
  const startComposition = () => setComposing(true);
  const endComposition = () => setComposing(false);

  const handleSelect = (id: string) => {
    const selectedNode = tree.get(id);
    if (selectedNode !== null) {
      setSelectedNodeId(id);
      onSelect(selectedNode.data);
    }
  };

  return (
    <div
      style={style}
      ref={dragHandle}
      onClick={(e) => {
        e.stopPropagation();
        handleSelect(node.id);
      }}
      className={`flex h-6 min-w-min flex-1 flex-row ${
        node.id === selectedNodeId ? "bg-selected" : ""
      }`}
    >
      <div
        className={`flex flex-1 flex-row  border border-solid border-gray-300`}
      >
        {node.isInternal && node.data.children.length > 0 && (
          <div className="flex flex-col text-gray-600">
            <button
              onClick={() => node.isInternal && node.toggle()}
              className={`h-8 w-6 border-none bg-transparent text-gray-600 ${
                node.isOpen ? "rotate-90" : ""
              }`}
            >
              ▶︎
            </button>
          </div>
        )}
        <div className="flex w-5 flex-col">
          <input
            className="my-auto"
            type="checkbox"
            checked={node.state.isSelected}
            onClick={(e) => e.stopPropagation()}
            onChange={() => {
              node.isSelected ? node.deselect() : node.selectMulti();
            }}
          />
        </div>
        <div className="flex flex-1 flex-col">
          <span className="my-auto flex">
            {node.isEditing ? (
              <input
                className="h-5 border-2 border-blue-200 text-xs"
                type="text"
                defaultValue={node.data.name}
                onFocus={(e) => e.currentTarget.select()}
                onBlur={() => node.reset()}
                onCompositionStart={startComposition}
                onCompositionEnd={endComposition}
                onClick={(e) => e.stopPropagation()}
                onKeyDown={(e) => {
                  if (e.key === "Enter") {
                    if (composing) return;
                    e.stopPropagation();
                    node.submit(e.currentTarget.value);
                  }
                }}
                autoFocus
              />
            ) : (
              <span className="items-center text-xs">{node.data.name}</span>
            )}
          </span>
        </div>
        <div className="mr-2 flex space-x-2">
          <Button
            onClick={(e) => {
              e.stopPropagation();
              node.edit();
            }}
            className="m-auto size-5 rounded-none border bg-white p-0 hover:bg-white hover:opacity-50"
          >
            <EditSvg />
          </Button>
          <Button
            onClick={(e) => {
              e.stopPropagation();
              tree.delete(node.id);
            }}
            className="m-auto size-5 rounded-none border bg-white p-0 hover:bg-white hover:opacity-50"
          >
            <DeleteSvg />
          </Button>
        </div>
      </div>
    </div>
  );
};
