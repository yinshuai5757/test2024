import { TreeNode } from "@/components/base/tree-node-list";
import { NodeItem } from "@/components/ui/tree-node/node-item";
import { Spacer } from "@/components/ui/tree-node/node-spacer";

type NodeListProps = {
  depth: number;
  rootId: string;
  treeNodes: TreeNode[];
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
  // onNodeSelect: (nodeName: string) => void;
};

export const NodeList = (props: NodeListProps) => {
  const {
    depth,
    rootId,
    treeNodes,
    isDragStarted,
    handleDelete,
    handleDragEnd,
    handleDragEnter,
    handleDragLeave,
    handleDragOver,
    handleDragStart,
    handleDrop,
    handleToggleCheck,
    handleToggleOpen,
    // onNodeSelect,
  } = props;

  const listItems = (
    nodes: TreeNode[],
    itemDepth: number = 0,
    parentId: string
  ) =>
    nodes.map((node, index, array) => (
      <div key={index}>
        <li key={`spacer-above-${node.id}`}>
          <Spacer
            depth={itemDepth}
            node={node}
            parentId={parentId}
            position={index === 0 ? "first" : "theOthers"}
            isDragStarted={isDragStarted}
            handleDragEnter={handleDragEnter}
            handleDragLeave={handleDragLeave}
            handleDragOver={handleDragOver}
            handleDrop={handleDrop}
          />
        </li>
        <li className="shrink-0 bg-white" key={`node-${node.id}`}>
          {node.children.length === 0 ? (
            <NodeItem
              depth={itemDepth}
              node={node}
              parentId={parentId}
              isDragStarted={isDragStarted}
              handleDelete={handleDelete}
              handleDragEnd={handleDragEnd}
              handleDragEnter={handleDragEnter}
              handleDragLeave={handleDragLeave}
              handleDragOver={handleDragOver}
              handleDragStart={handleDragStart}
              handleDrop={handleDrop}
              handleToggleCheck={handleToggleCheck}
              handleToggleOpen={handleToggleOpen}
            />
          ) : (
            <div>
              <div>
                <NodeItem
                  depth={itemDepth}
                  node={node}
                  parentId={parentId}
                  isDragStarted={isDragStarted}
                  handleDelete={handleDelete}
                  handleDragEnd={handleDragEnd}
                  handleDragEnter={handleDragEnter}
                  handleDragLeave={handleDragLeave}
                  handleDragOver={handleDragOver}
                  handleDragStart={handleDragStart}
                  handleDrop={handleDrop}
                  handleToggleCheck={handleToggleCheck}
                  handleToggleOpen={handleToggleOpen}
                />
              </div>
              {node.isOpen && (
                <ul className="m-0 list-none pl-0">
                  {listItems(node.children, itemDepth + 1, node.id)}
                </ul>
              )}
            </div>
          )}
        </li>
        {index === array.length - 1 && (
          <li key={`spacer-below-${node.id}`}>
            <Spacer
              depth={itemDepth}
              node={null}
              parentId={parentId}
              position={"last"}
              isDragStarted={isDragStarted}
              handleDragEnter={handleDragEnter}
              handleDragLeave={handleDragLeave}
              handleDragOver={handleDragOver}
              handleDrop={handleDrop}
            />
          </li>
        )}
      </div>
    ));

  return (
    <ul className="m-0 list-none pl-0">
      {listItems(treeNodes, depth, rootId)}
    </ul>
  );
};
