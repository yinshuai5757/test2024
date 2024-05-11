import { useRef, useState } from "react";
import { Button } from "../ui/button";
import { Tree } from "react-arborist";
import { ArboristNodeType } from "@/app/page";
import { Node } from "@/components/ui/tree-node/node";
import { AddSvg } from "@/data/image/add-svg";
import { TrashSvg } from "@/data/image/trash-svg";

type TreeViewProps = {
  data: ArboristNodeType[];
  loading: boolean;
  templateId: number;
  onSelect: (nodeData: ArboristNodeType) => void;
};

export const TreeView = ({
  data,
  loading,
  templateId,
  onSelect,
}: TreeViewProps) => {
  console.log(data);
  const treeRef = useRef<any>(null);
  const [selectedNodeId, setSelectedNodeId] = useState("");

  const clearSelectedNodes = () => {
    const tree = treeRef.current;
    if (!tree) return;
    const selectedIds = tree.selectedIds;
    selectedIds.forEach((id: string) => {
      tree.delete(id);
    });
  };

  return (
    <>
      <div className="flex-1 basis-0 overflow-y-scroll p-4">
        <div className="mx-auto">
          {loading ? (
            <p>Loading...</p>
          ) : (
            <Tree
              ref={treeRef}
              initialData={data ? data : []}
              rowHeight={28}
              width="100%"
            >
              {(props) => (
                <Node
                  {...props}
                  onSelect={onSelect}
                  selectedNodeId={selectedNodeId}
                  setSelectedNodeId={setSelectedNodeId}
                />
              )}
            </Tree>
          )}
        </div>
      </div>
      <div className="flex justify-end space-x-2 border p-2">
        <Button
          className={`button-svg-gray ${
            templateId === 0
              ? "bg-disabled"
              : "bg-inactive hover:bg-brand hover:opacity-70"
          }`}
          disabled={templateId === 0 ? true : false}
          onClick={() => {
            treeRef.current.create({
              type: "internal",
              parentId: selectedNodeId,
            });
            setSelectedNodeId("");
          }}
        >
          <AddSvg />
        </Button>
        <Button
          className={`button-svg-gray ${
            templateId === 0
              ? "bg-disabled"
              : "bg-inactive hover:bg-brand hover:opacity-70"
          }`}
          disabled={templateId === 0 ? true : false}
          onClick={clearSelectedNodes}
        >
          <TrashSvg />
        </Button>
      </div>
    </>
  );
};
