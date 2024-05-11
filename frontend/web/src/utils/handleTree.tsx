import { TreeNode } from "@/components/base/tree-node-list";

export const isParent = (
  root: TreeNode,
  targetNodeId: string,
  maybeParentNodeId: string
): boolean => {
  const parent = findNode(root, maybeParentNodeId);
  if (parent) {
    const target = findNode(parent, targetNodeId);
    if (target) {
      return true;
    }
  }
  return false;
};

export const addNode = (root: TreeNode, node: TreeNode): TreeNode => {
  return { ...root, children: [node, ...root.children] };
};

export const deleteNode = (root: TreeNode, nodeId: string): TreeNode => {
  const f = (node: TreeNode) => {
    if (node.children.length >= 1) {
      const idx = node.children.findIndex((n) => n.id === nodeId);
      idx >= 0 ? node.children.splice(idx, 1) : node.children.map((c) => f(c));
    }
  };
  f(root);
  return root;
};

export const findNode = (
  root: TreeNode,
  nodeId: string
): TreeNode | undefined => {
  const f = (node: TreeNode): TreeNode | undefined => {
    if (root.id === nodeId) {
      return node;
    } else if (node.children.length >= 1) {
      const found = node.children.find((n) => n.id === nodeId);
      if (found) {
        return found;
      } else {
        for (const n of node.children) {
          const result = f(n);
          if (result) {
            return result;
          }
        }
      }
    } else {
      return undefined;
    }
  };
  return f(root);
};

export const moveToFirstChild = (
  root: TreeNode,
  targetNodeId: string,
  parentNodeId: string
) => {
  const found = findNode(root, targetNodeId);
  const parent = findNode(root, parentNodeId);
  if (found && parent) {
    deleteNode(root, found.id);
    parent.children.splice(0, 0, found);
  }
  return root;
};

export const moveToLastChild = (
  root: TreeNode,
  targetNodeId: string,
  parentNodeId: string
) => {
  const found = findNode(root, targetNodeId);
  const parent = findNode(root, parentNodeId);
  if (found && parent) {
    deleteNode(root, found.id);
    parent.children.push(found);
  }
  return root;
};

export const moveBetweenNodes = (
  root: TreeNode,
  targetNodeId: string,
  parentNodeId: string,
  nextNodeId: string
) => {
  const found = findNode(root, targetNodeId);
  const parent = findNode(root, parentNodeId);
  if (found && parent) {
    deleteNode(root, found.id);
    const idx = parent.children.findIndex((c) => c.id === nextNodeId);
    parent.children.splice(idx, 0, found);
  }
  return root;
};

export const toggleNodeCompleted = (
  root: TreeNode,
  nodeId: string
): TreeNode => {
  const f = (node: TreeNode) => {
    if (node.children.length >= 1) {
      const idx = node.children.findIndex((n) => n.id === nodeId);
      idx >= 0
        ? node.children.splice(idx, 1, {
            ...node.children[idx],
            isCompleted: !node.children[idx].isCompleted,
          })
        : node.children.map((c) => f(c));
    }
  };
  f(root);
  return root;
};

export const toggleNodeOpen = (root: TreeNode, nodeId: string): TreeNode => {
  const f = (node: TreeNode) => {
    if (node.children.length >= 1) {
      const idx = node.children.findIndex((n) => n.id === nodeId);
      idx >= 0
        ? node.children.splice(idx, 1, {
            ...node.children[idx],
            isOpen: !node.children[idx].isOpen,
          })
        : node.children.map((c) => f(c));
    }
  };
  f(root);
  return root;
};
