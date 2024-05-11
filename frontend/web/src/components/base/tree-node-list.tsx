import {
  isParent,
  addNode,
  deleteNode,
  moveToFirstChild,
  moveToLastChild,
  moveBetweenNodes,
  toggleNodeCompleted,
  toggleNodeOpen,
} from "@/utils/handleTree";
import { useState } from "react";
import { NodeList } from "@/components/ui/tree-node/node-list";
import { Button } from "../ui/button";
import { TrashSvg } from "@/data/image/trash-svg";

export type TreeNode = {
  id: string;
  name: string;
  sample_format: string;
  sample_generated_text: string;
  isCompleted: boolean;
  isOpen: boolean;
  children: TreeNode[];
};

export type TreeNodeListProps = {};

export type DropTargetType = "node" | "spacer";

// 木構造のツリービューコンポーネント
export const TreeNodeList = () => {
  const [draggingId, setDraggingId] = useState<string | null>(null);
  const [newTaskName, setNewTaskName] = useState("");
  const [treeNode, setTreeNode] = useState<TreeNode>({
    id: "root",
    name: "",
    sample_format: "",
    sample_generated_text: "",
    isCompleted: false,
    isOpen: true,
    children: [],
  });

  const canDrop = (
    root: TreeNode,
    draggingNodeId: string,
    dropTargetNodeId: string
  ): boolean => {
    if (!isParent(root, dropTargetNodeId, draggingNodeId)) {
      return true;
    }
    return false;
  };

  const onInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    setNewTaskName(e.currentTarget.value);
  };

  const onSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const id = Math.floor(Math.random() * 10000).toString();
    const newNode: TreeNode = {
      id: id,
      name: newTaskName || "新しい条項",
      sample_format: "",
      sample_generated_text: "",
      isCompleted: false,
      isOpen: true,
      children: [],
    };
    setTreeNode({ ...addNode(treeNode, newNode) });
    setNewTaskName("");
  };

  const handleClickClear = (e: React.MouseEvent<HTMLButtonElement>) => {
    setTreeNode({ ...treeNode, children: [] });
  };

  const handleDelete = (e: React.MouseEvent<HTMLButtonElement>) => {
    const nodeId = e.currentTarget.dataset.nodeId;
    if (nodeId) {
      if (confirm("本当に削除してもよろしいですか？")) {
        setTreeNode({ ...deleteNode(treeNode, nodeId) });
      }
    }
  };

  const handleDragEnd = (e: React.DragEvent<HTMLDivElement>) => {
    setDraggingId(null);
  };

  const handleDragEnter = (e: React.DragEvent<HTMLDivElement>) => {
    const { first, last, parentId, nextId, nodeId, dropTargetType } =
      e.currentTarget.dataset;
    if (draggingId && parentId) {
      if (dropTargetType === "node") {
        canDrop(treeNode, draggingId, parentId)
          ? e.currentTarget.classList.add("droppable-node")
          : e.currentTarget.classList.add("undroppable-node");
      } else if (dropTargetType === "spacer") {
        canDrop(treeNode, draggingId, parentId)
          ? e.currentTarget.classList.add("droppable-spacer")
          : e.currentTarget.classList.add("undroppable-spacer");
      }
    }
  };

  const handleDragLeave = (e: React.DragEvent<HTMLDivElement>) => {
    removeDroppableStyles(e.currentTarget);
  };

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault(); // enable drop event
  };

  const handleDragStart = (e: React.DragEvent<HTMLDivElement>) => {
    setDraggingId(e.currentTarget.dataset.nodeId || null);
  };

  const removeDroppableStyles = (target: HTMLDivElement) => {
    target.classList.remove("droppable-node");
    target.classList.remove("undroppable-node");
    target.classList.remove("droppable-spacer");
    target.classList.remove("undroppable-spacer");
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    const { first, last, dropTargetType } = e.currentTarget.dataset;
    const nodeId = e.currentTarget.dataset.nodeId;
    const parentId = e.currentTarget.dataset.parentId;
    const nextId = e.currentTarget.dataset.nextId;
    if (draggingId && parentId) {
      if (
        dropTargetType === "node" &&
        nodeId &&
        canDrop(treeNode, draggingId, nodeId)
      ) {
        setTreeNode({ ...moveToFirstChild(treeNode, draggingId, nodeId) });
      } else if (dropTargetType === "spacer") {
        if (first && canDrop(treeNode, draggingId, parentId)) {
          setTreeNode({ ...moveToFirstChild(treeNode, draggingId, parentId) });
        } else if (last && canDrop(treeNode, draggingId, parentId)) {
          setTreeNode({ ...moveToLastChild(treeNode, draggingId, parentId) });
        } else if (nextId && canDrop(treeNode, draggingId, nextId)) {
          setTreeNode({
            ...moveBetweenNodes(treeNode, draggingId, parentId, nextId),
          });
        }
      }
    }
    removeDroppableStyles(e.currentTarget);
  };

  const handleToggleCheck = (e: React.MouseEvent<HTMLInputElement>) => {
    const nodeId = e.currentTarget.dataset.nodeId;
    if (nodeId) {
      setTreeNode({ ...toggleNodeCompleted(treeNode, nodeId) });
    }
  };

  const handleToggleOpen = (e: React.MouseEvent<HTMLElement>) => {
    const nodeId = e.currentTarget.dataset.nodeId;
    if (nodeId) {
      setTreeNode({ ...toggleNodeOpen(treeNode, nodeId) });
    }
  };

  return (
    <>
      <div className="flex-1 basis-0 overflow-y-scroll p-4">
        <div className="mx-auto">
          <NodeList
            depth={0}
            treeNodes={treeNode.children}
            rootId={treeNode.id}
            isDragStarted={draggingId ? true : false}
            handleDelete={handleDelete}
            handleDragEnd={handleDragEnd}
            handleDragEnter={handleDragEnter}
            handleDragLeave={handleDragLeave}
            handleDragOver={handleDragOver}
            handleDragStart={handleDragStart}
            handleDrop={handleDrop}
            handleToggleCheck={handleToggleCheck}
            handleToggleOpen={handleToggleOpen}
            // onNodeSelect={onNodeSelect}
          />
        </div>
      </div>
      <div className="flex space-x-2 p-2">
        <form className="flex flex-1" onSubmit={onSubmit}>
          <input
            type="text"
            onInput={onInput}
            value={newTaskName}
            placeholder="追加する条項を入力してください"
            className="shadow-textarea grow border px-2"
          />
        </form>
        <Button
          onClick={handleClickClear}
          className="bg-brand hover:bg-brand text-white hover:opacity-70"
        >
          <TrashSvg />
        </Button>
      </div>
    </>
  );
};
